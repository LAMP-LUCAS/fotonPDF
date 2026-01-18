"""
Menu Interativo - Interface amigável para execução direta do fotonPDF
Exibido quando o executável é aberto sem argumentos.
"""
import click
import sys
from src.infrastructure.services.logger import log_info, log_exception


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
    click.echo("  [5] ❌ Sair")
    click.echo()


def run_interactive_menu():
    """Executa o menu interativo principal."""
    log_info("Menu interativo iniciado")
    
    while True:
        print_header()
        print_menu_options()
        
        choice = click.prompt("  Escolha uma opção", type=click.IntRange(1, 5), default=1)
        
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
