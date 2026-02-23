"""
Uninstall Wizard - Assistente de Desinstalação do fotonPDF
Fornece feedback visual passo a passo durante o processo de offboarding.
"""
import click
from src.infrastructure.services.logger import log_info, log_error, log_warning, log_debug
# Removida dependência direta de infraestrutura (WindowsRegistryAdapter) para seguir Arquitetura Hexagonal.


def print_header():
    """Exibe o cabeçalho do wizard."""
    from src import __version__
    click.echo()
    click.secho("╔═══════════════════════════════════════════════════════════╗", fg='yellow')
    click.secho(f"║     fotonPDF v{__version__} - Assistente de Desinstalação      ║", fg='yellow')
    click.secho("╚═══════════════════════════════════════════════════════════╝", fg='yellow')
    click.echo()
    log_info(f"Uninstall Wizard iniciado (v{__version__})")


def print_step(step: int, total: int, message: str):
    """Exibe uma etapa do wizard."""
    click.echo(f"[{step}/{total}] {message}")
    log_debug(f"Etapa {step}/{total}: {message}")


def print_success(message: str):
    """Exibe mensagem de sucesso."""
    click.secho(f"      ✅ {message}", fg='green')
    log_info(f"✓ {message}")


def print_error(message: str):
    """Exibe mensagem de erro."""
    click.secho(f"      ❌ {message}", fg='red')
    log_error(f"✗ {message}")


def print_warning(message: str):
    """Exibe mensagem de aviso."""
    click.secho(f"      ⚠️  {message}", fg='yellow')
    log_warning(f"⚠ {message}")


def print_footer_success():
    """Exibe o rodapé de sucesso."""
    click.echo()
    click.secho("════════════════════════════════════════════════════════════", fg='green')
    click.secho("✅ Desinstalação concluída! O fotonPDF foi removido do sistema.", fg='green')
    click.secho("   Obrigado por usar o fotonPDF. Até a próxima! 👋", fg='cyan')
    click.secho("════════════════════════════════════════════════════════════", fg='green')
    click.echo()
    log_info("Desinstalação concluída com sucesso")


def print_footer_error():
    """Exibe o rodapé de erro."""
    click.echo()
    click.secho("════════════════════════════════════════════════════════════", fg='red')
    click.secho("❌ Desinstalação falhou. Verifique as mensagens acima.", fg='red')
    click.secho("   Dica: Tente executar como Administrador.", fg='yellow')
    click.secho("════════════════════════════════════════════════════════════", fg='red')
    click.echo()
    log_error("Desinstalação falhou")


def wait_for_keypress():
    """Aguarda o usuário pressionar uma tecla antes de fechar."""
    click.echo()
    click.pause("Pressione qualquer tecla para sair...")


def confirm_removal() -> bool:
    """Pede confirmação do usuário antes de remover."""
    click.echo("⚠️  Esta ação irá remover o fotonPDF do Menu de Contexto.")
    return click.confirm("   Deseja continuar?", default=False)


def unregister_all_os_integrations() -> bool:
    """Remove o fotonPDF do registro e atalhos via Use Case."""
    from src.application.use_cases.unregister_os import UnregisterOSIntegrationUseCase
    from src.infrastructure.adapters.windows_registry_adapter import WindowsRegistryAdapter
    
    log_debug("Iniciando limpeza completa do sistema...")
    adapter = WindowsRegistryAdapter()
    use_case = UnregisterOSIntegrationUseCase(adapter)
    return use_case.execute()


def verify_removal() -> bool:
    """Verifica se o fotonPDF foi removido corretamente."""
    from src.infrastructure.adapters.windows_registry_adapter import WindowsRegistryAdapter
    adapter = WindowsRegistryAdapter()
    result = not adapter.check_installation_status()
    log_debug(f"Verificação de remoção: {'OK' if result else 'Ainda instalado'}")
    return result


def run_uninstall(skip_confirmation: bool = False) -> bool:
    """Executa o wizard de desinstalação completo."""
    try:
        print_header()
        
        # Confirmação
        if not skip_confirmation:
            if not confirm_removal():
                click.echo()
                click.secho("   Operação cancelada pelo usuário.", fg='yellow')
                log_info("Desinstalação cancelada pelo usuário")
                click.echo()
                wait_for_keypress()
                return False
        
        click.echo()
        total_steps = 2
        
        # Etapa 1: Limpeza do Sistema
        print_step(1, total_steps, "Removendo registros e atalhos do sistema...")
        
        if unregister_all_os_integrations():
            print_success("Registros e atalhos removidos com sucesso")
        else:
            print_error("Houve uma falha parcial na remoção (verifique permissões)")
            print_footer_error()
            if not skip_confirmation: wait_for_keypress()
            return False

        # Etapa 3: Verificar Remoção
        print_step(3, total_steps, "Verificando remoção...")
        if verify_removal():
            print_success("Remoção verificada com sucesso")
        else:
            print_warning("Pode ser necessário reiniciar o Windows Explorer")
        
        print_footer_success()
        if not skip_confirmation: wait_for_keypress()
        return True
        
    except Exception as e:
        from src.infrastructure.services.logger import log_exception
        log_exception(f"Erro inesperado no uninstall: {e}")
        print_error(f"Erro inesperado: {e}")
        print_footer_error()
        if not skip_confirmation: wait_for_keypress()
        return False
