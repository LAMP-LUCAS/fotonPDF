"""
Uninstall Wizard - Assistente de Desinstalação do fotonPDF
Fornece feedback visual passo a passo durante o processo de offboarding.
"""
import click


def print_header():
    """Exibe o cabeçalho do wizard."""
    from src import __version__
    click.echo()
    click.secho("╔═══════════════════════════════════════════════════════════╗", fg='yellow')
    click.secho(f"║     fotonPDF v{__version__} - Assistente de Desinstalação      ║", fg='yellow')
    click.secho("╚═══════════════════════════════════════════════════════════╝", fg='yellow')
    click.echo()


def print_step(step: int, total: int, message: str):
    """Exibe uma etapa do wizard."""
    click.echo(f"[{step}/{total}] {message}")


def print_success(message: str):
    """Exibe mensagem de sucesso."""
    click.secho(f"      ✅ {message}", fg='green')


def print_error(message: str):
    """Exibe mensagem de erro."""
    click.secho(f"      ❌ {message}", fg='red')


def print_warning(message: str):
    """Exibe mensagem de aviso."""
    click.secho(f"      ⚠️  {message}", fg='yellow')


def print_footer_success():
    """Exibe o rodapé de sucesso."""
    click.echo()
    click.secho("════════════════════════════════════════════════════════════", fg='green')
    click.secho("✅ Desinstalação concluída! O fotonPDF foi removido do sistema.", fg='green')
    click.secho("   Obrigado por usar o fotonPDF. Até a próxima! 👋", fg='cyan')
    click.secho("════════════════════════════════════════════════════════════", fg='green')
    click.echo()


def print_footer_error():
    """Exibe o rodapé de erro."""
    click.echo()
    click.secho("════════════════════════════════════════════════════════════", fg='red')
    click.secho("❌ Desinstalação falhou. Verifique as mensagens acima.", fg='red')
    click.secho("   Dica: Tente executar como Administrador.", fg='yellow')
    click.secho("════════════════════════════════════════════════════════════", fg='red')
    click.echo()


def confirm_removal() -> bool:
    """Pede confirmação do usuário antes de remover."""
    click.echo("⚠️  Esta ação irá remover o fotonPDF do Menu de Contexto.")
    return click.confirm("   Deseja continuar?", default=False)


def unregister_context_menu() -> bool:
    """Remove o fotonPDF do menu de contexto."""
    from src.application.use_cases.unregister_os import UnregisterOSIntegrationUseCase
    from src.infrastructure.adapters.windows_registry_adapter import WindowsRegistryAdapter
    
    adapter = WindowsRegistryAdapter()
    use_case = UnregisterOSIntegrationUseCase(adapter)
    return use_case.execute()


def verify_removal() -> bool:
    """Verifica se o fotonPDF foi removido corretamente."""
    from src.infrastructure.adapters.windows_registry_adapter import WindowsRegistryAdapter
    adapter = WindowsRegistryAdapter()
    # Se não estiver instalado, a remoção foi bem-sucedida
    return not adapter.check_installation_status()


def run_uninstall(skip_confirmation: bool = False) -> bool:
    """Executa o wizard de desinstalação completo."""
    print_header()
    
    # Confirmação
    if not skip_confirmation:
        if not confirm_removal():
            click.echo()
            click.secho("   Operação cancelada pelo usuário.", fg='yellow')
            click.echo()
            return False
    
    click.echo()
    total_steps = 2
    
    # Etapa 1: Remover Menu de Contexto
    print_step(1, total_steps, "Removendo do Menu de Contexto do Windows...")
    
    if unregister_context_menu():
        print_success("Entradas do registro removidas")
    else:
        print_error("Falha ao remover do registro")
        print_footer_error()
        return False
    
    # Etapa 2: Verificar Remoção
    print_step(2, total_steps, "Verificando remoção...")
    if verify_removal():
        print_success("Remoção verificada com sucesso")
    else:
        print_warning("Pode ser necessário reiniciar o Windows Explorer")
    
    print_footer_success()
    return True
