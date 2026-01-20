"""
Menu Interativo - Interface amigável para execução direta do fotonPDF
Exibido quando o executável é aberto sem argumentos.
"""
import click
import sys
from src.infrastructure.services.logger import log_info, log_exception
from src.application.services.update_service import UpdateService


def print_header():
    """Exibe o cabeçalho do menu."""
    from src import __version__
    click.clear()
    click.echo()
    click.secho("╔═══════════════════════════════════════════════════════════╗", fg='cyan')
    click.secho(f"║              fotonPDF v{__version__} - Menu Principal            ║", fg='cyan')
    click.secho("╚═══════════════════════════════════════════════════════════╝", fg='cyan')
    click.echo()


def print_menu_options():
    """Exibe as opções do menu."""
    click.echo("  [1] 🚀 Configurar fotonPDF (Setup)")
    click.echo("  [2] 📄 Abrir Visualizador de PDFs")
    click.echo("  [3] 📊 Verificar Status da Instalação")
    click.echo("  [4] 🗑️  Remover fotonPDF")
    click.echo("  [R] 🔧 Reparar Integração (Bootstrap)")
    click.echo("  [A] 🔗 Criar Atalhos (Desktop/Menu Iniciar)")
    click.echo("  [D] 📌 Definir como Visualizador Padrão")
    click.echo("  [5] ❌ Sair")
    click.echo()
def check_updates_silent():
    """Verifica atualizações e mostra apenas se houver novidade."""
    try:
        service = UpdateService()
        new_version = service.check_for_updates()
        if new_version:
            click.echo()
            click.secho(f"  🔔 Uma nova versão está disponível: v{new_version['version']}", fg='green', bold=True)
            click.secho(f"  💡 Execute 'foton update' para ver detalhes.", fg='yellow')
            click.echo()
    except Exception:
        pass


def run_interactive_menu():
    """Executa o menu interativo principal."""
    log_info("Menu interativo iniciado")
    
    # Verificação rápida de atualização no início
    check_updates_silent()
    
    while True:
        print_header()
        print_menu_options()
        
        choice = click.prompt("  Escolha uma opção", type=click.Choice(['1', '2', '3', '4', '5', 'r', 'R', 'a', 'A', 'd', 'D']), default='1')
        
        # Converter para int se for número para manter compatibilidade com a lógica anterior
        if choice.isdigit():
            choice = int(choice)

        if choice == 1:
            # Setup
            click.echo()
            from src.interfaces.cli.setup_wizard import run_setup
            run_setup()
            return  # Sair após setup
            
        elif choice == 2:
            # Abrir Visualizador
            click.echo()
            click.echo("  🚀 Abrindo Visualizador...")
            log_info("Abrindo visualizador via menu")
            try:
                from src.interfaces.gui.app import main
                main()
            except Exception as e:
                log_exception(f"Erro ao abrir visualizador no menu: {e}")
                click.secho(f"  ❌ Erro ao abrir visualizador: {e}", fg='red')
                click.pause()
            return  # Sair após abrir
            
        elif choice == 3:
            # Verificar Status
            click.echo()
            show_detailed_status()
            click.echo()
            click.pause("  Pressione qualquer tecla para continuar...")
        elif choice == 4:
            # Remover
            click.echo()
            from src.interfaces.cli.uninstall_wizard import run_uninstall
            run_uninstall()
            return  # Sair após remover
            
        elif choice == 'r' or choice == 'R':
            # Reparar
            click.echo()
            click.echo("  🔧 Iniciando Reparo Inteligente...")
            from src.infrastructure.adapters.windows_registry_adapter import WindowsRegistryAdapter
            adapter = WindowsRegistryAdapter()
            if adapter.repair_installation():
                click.secho("  ✅ Reparo concluído com sucesso!", fg='green')
            else:
                click.secho("  ❌ Ocorreu um erro durante o reparo.", fg='red')
            click.pause("\n  Pressione qualquer tecla para continuar...")

        elif choice.lower() == 'a':
            # Atalhos
            click.echo()
            from src.application.use_cases.register_os import RegisterOSIntegrationUseCase
            from src.infrastructure.adapters.windows_registry_adapter import WindowsRegistryAdapter
            
            use_case = RegisterOSIntegrationUseCase(WindowsRegistryAdapter())
            if use_case.create_shortcut("desktop"):
                click.secho("  ✅ Atalho criado na Área de Trabalho!", fg='green')
            if use_case.create_shortcut("start_menu"):
                click.secho("  ✅ Atalho criado no Menu Iniciar!", fg='green')
            click.pause("\n  Pressione qualquer tecla para continuar...")

        elif choice.lower() == 'd':
            # Programa Padrão
            click.echo()
            from src.application.use_cases.register_os import RegisterOSIntegrationUseCase
            from src.infrastructure.adapters.windows_registry_adapter import WindowsRegistryAdapter
            
            use_case = RegisterOSIntegrationUseCase(WindowsRegistryAdapter())
            if use_case.set_as_default():
                click.secho("  ✅ fotonPDF registrado como visualizador padrão!", fg='green')
                click.secho("  💡 O Windows pode pedir confirmação ao abrir o próximo PDF.", fg='yellow')
            else:
                click.secho("  ❌ Falha ao definir programa padrão.", fg='red')
            click.pause("\n  Pressione qualquer tecla para continuar...")

        elif choice == 5:
            # Sair
            click.echo()
            click.secho("  Até logo! 👋", fg='cyan')
            click.echo()
            return


def show_detailed_status():
    """Mostra status detalhado da instalação."""
    from src import __version__
    from src.infrastructure.adapters.windows_registry_adapter import WindowsRegistryAdapter
    
    click.secho("  ╔══════════════════════════════════════╗", fg='cyan')
    click.secho("  ║        Status da Instalação          ║", fg='cyan')
    click.secho("  ╚══════════════════════════════════════╝", fg='cyan')
    click.echo()
    
    click.echo(f"  Versão: {__version__}")
    
    adapter = WindowsRegistryAdapter()
    is_installed = adapter.check_installation_status()
    
    click.echo("  Menu de Contexto: ", nl=False)
    if is_installed:
        click.secho("✅ Instalado", fg='green')
        
        # Mostrar comando registrado
        cmd = adapter.get_registered_command()
        if cmd:
            click.echo(f"  Comando: {cmd[:50]}..." if len(cmd) > 50 else f"  Comando: {cmd}")
    else:
        click.secho("❌ Não instalado", fg='red')
        click.echo()
        click.secho("  💡 Dica: Escolha a opção 1 para configurar.", fg='yellow')
    
    # Mostrar caminho do executável
    if getattr(sys, 'frozen', False):
        click.echo(f"  Executável: {sys.executable}")
    else:
        click.echo("  Modo: Desenvolvimento (Python)")
