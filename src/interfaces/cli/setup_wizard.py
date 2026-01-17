"""
Setup Wizard - Assistente de Instalação do fotonPDF
Fornece feedback visual passo a passo durante o processo de onboarding.
"""
import sys
import click
from pathlib import Path
from src.infrastructure.services.logger import log_info, log_error, log_warning, log_debug


def print_header():
    """Exibe o cabeçalho do wizard."""
    from src import __version__
    click.echo()
    click.secho("╔═══════════════════════════════════════════════════════════╗", fg='cyan')
    click.secho(f"║       fotonPDF v{__version__} - Assistente de Setup            ║", fg='cyan')
    click.secho("╚═══════════════════════════════════════════════════════════╝", fg='cyan')
    click.echo()
    log_info(f"Setup Wizard iniciado (v{__version__})")


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
    click.secho("🎉 Setup concluído! Agora você pode clicar com o botão", fg='green')
    click.secho("   direito em qualquer PDF e escolher \"Abrir com fotonPDF\".", fg='green')
    click.secho("════════════════════════════════════════════════════════════", fg='green')
    click.echo()
    log_info("Setup concluído com sucesso")


def print_footer_error():
    """Exibe o rodapé de erro."""
    click.echo()
    click.secho("════════════════════════════════════════════════════════════", fg='red')
    click.secho("❌ Setup falhou. Verifique as mensagens acima e tente novamente.", fg='red')
    click.secho("   Dica: Tente executar como Administrador.", fg='yellow')
    click.secho("════════════════════════════════════════════════════════════", fg='red')
    click.echo()
    log_error("Setup falhou")


def wait_for_keypress():
    """Aguarda o usuário pressionar uma tecla antes de fechar."""
    click.echo()
    click.pause("Pressione qualquer tecla para sair...")


def check_permissions() -> bool:
    """Verifica se o usuário tem permissões de escrita no registro."""
    import winreg
    try:
        # Tenta abrir uma chave de teste com permissão de escrita
        test_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\fotonPDF_test")
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, r"Software\fotonPDF_test")
        return True
    except PermissionError:
        log_error("Permissão negada ao tentar escrever no registro")
        return False
    except Exception as e:
        log_debug(f"Verificação de permissão: {e}")
        return True  # Assume que está ok se não for erro de permissão


def get_app_command() -> tuple[Path, str]:
    """Detecta o caminho do executável e monta o comando."""
    if getattr(sys, 'frozen', False):
        app_path = Path(sys.executable)
        command = f'"{app_path}" view "%1"'
        log_debug(f"Modo frozen: {app_path}")
    else:
        app_path = Path(sys.argv[0]).absolute()
        command = f'python "{app_path}" view "%1"'
        log_debug(f"Modo desenvolvimento: {app_path}")
    return app_path, command


def register_context_menu(command: str) -> bool:
    """Registra o fotonPDF no menu de contexto."""
    from src.application.use_cases.register_os import RegisterOSIntegrationUseCase
    from src.infrastructure.adapters.windows_registry_adapter import WindowsRegistryAdapter
    
    log_debug(f"Registrando comando: {command}")
    adapter = WindowsRegistryAdapter()
    use_case = RegisterOSIntegrationUseCase(adapter)
    return use_case.execute("Abrir com fotonPDF", command)


def verify_installation() -> bool:
    """Verifica se o fotonPDF está corretamente instalado."""
    from src.infrastructure.adapters.windows_registry_adapter import WindowsRegistryAdapter
    adapter = WindowsRegistryAdapter()
    result = adapter.check_installation_status()
    log_debug(f"Verificação de instalação: {'OK' if result else 'Não encontrado'}")
    return result


def run_setup() -> bool:
    """Executa o wizard de setup completo."""
    try:
        print_header()
        
        total_steps = 3
        
        # Etapa 1: Verificar Permissões
        print_step(1, total_steps, "Verificando permissões do sistema...")
        if check_permissions():
            print_success("Permissões OK")
        else:
            print_error("Sem permissão de escrita no registro")
            print_warning("Tente executar como Administrador")
            print_footer_error()
            wait_for_keypress()
            return False
        
        # Etapa 2: Registrar Menu de Contexto
        print_step(2, total_steps, "Registrando no Menu de Contexto do Windows...")
        app_path, command = get_app_command()
        
        if register_context_menu(command):
            print_success('"Abrir com fotonPDF" adicionado com sucesso')
        else:
            print_error("Falha ao registrar no Menu de Contexto")
            print_footer_error()
            wait_for_keypress()
            return False
        
        # Etapa 3: Verificar Integridade
        print_step(3, total_steps, "Verificando integridade da instalação...")
        if verify_installation():
            print_success("Instalação verificada e funcional")
        else:
            print_warning("Não foi possível confirmar a instalação")
            print_warning("Reinicie o Windows Explorer ou o computador")
        
        print_footer_success()
        wait_for_keypress()
        return True
        
    except Exception as e:
        from src.infrastructure.services.logger import log_exception
        log_exception(f"Erro inesperado no setup: {e}")
        print_error(f"Erro inesperado: {e}")
        print_footer_error()
        wait_for_keypress()
        return False
