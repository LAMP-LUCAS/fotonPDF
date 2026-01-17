import click
from pathlib import Path
from src.infrastructure.adapters.pymupdf_adapter import PyMuPDFAdapter
from src.infrastructure.adapters.notification_adapter import PlyerNotificationAdapter
from src.application.use_cases.rotate_pdf import RotatePDFUseCase
from src.application.use_cases.merge_pdf import MergePDFUseCase
from src.application.use_cases.split_pdf import SplitPDFUseCase

def notify_success(title: str, msg: str):
    click.secho(f"✅ {msg}", fg='green')
    PlyerNotificationAdapter().notify(title, msg)

def notify_error(msg: str):
    click.secho(f"❌ Erro: {msg}", fg='red', err=True)
    PlyerNotificationAdapter().notify("Erro no fotonPDF", msg)

@click.group()
def cli():
    """fotonPDF - O toolkit de PDFs mais rápido do mundo! 🚀"""
    pass

@cli.command()
@click.argument('path', type=click.Path(exists=True, path_type=Path))
@click.option('--degrees', '-d', type=int, default=90, help='Angulo de rotação (90, 180, 270)')
def rotate(path: Path, degrees: int):
    """Gira todas as páginas de um arquivo PDF."""
    try:
        adapter = PyMuPDFAdapter()
        use_case = RotatePDFUseCase(adapter)
        
        click.echo(f"🔄 Rotacionando {path.name} em {degrees}°...")
        output_path = use_case.execute(path, degrees)
        notify_success("Rotação Concluída", f"Arquivo salvo em: {output_path.name}")
        
    except Exception as e:
        notify_error(str(e))

@cli.command()
@click.argument('paths', nargs=-1, type=click.Path(exists=True, path_type=Path), required=True)
@click.option('--output', '-o', type=click.Path(path_type=Path), help='Caminho de saída')
def merge(paths: tuple[Path, ...], output: Path | None):
    """Une múltiplos arquivos PDF em um só."""
    try:
        if not output:
            output = paths[0].parent / "merged.pdf"
            
        adapter = PyMuPDFAdapter()
        use_case = MergePDFUseCase(adapter)
        
        click.echo(f"📑 Unindo {len(paths)} arquivos...")
        output_path = use_case.execute(list(paths), output)
        notify_success("União Concluída", f"Arquivo unido: {output_path.name}")
        
    except Exception as e:
        notify_error(str(e))

@cli.command()
@click.argument('path', type=click.Path(exists=True, path_type=Path))
@click.option('--pages', '-p', required=True, help='Páginas para extrair (ex: 1,2,5-8)')
@click.option('--output', '-o', type=click.Path(path_type=Path), help='Caminho de saída')
def split(path: Path, pages: str, output: Path | None):
    """Extrai páginas específicas de um PDF."""
    try:
        page_list = []
        for part in pages.split(','):
            if '-' in part:
                start, end = map(int, part.split('-'))
                page_list.extend(range(start, end + 1))
            else:
                page_list.append(part)
        
        # Garantir converter para int
        page_list = [int(p) for p in page_list]

        if not output:
            output = path.parent / f"{path.stem}_split{path.suffix}"

        adapter = PyMuPDFAdapter()
        use_case = SplitPDFUseCase(adapter)
        
        click.echo(f"✂️ Extraindo páginas {pages} de {path.name}...")
        output_path = use_case.execute(path, page_list, output)
        notify_success("Extração Concluída", f"Páginas extraídas em: {output_path.name}")
        
    except Exception as e:
        notify_error(str(e))

@cli.command()
@click.argument('path', type=click.Path(exists=True, path_type=Path), required=False)
def view(path: Path | None):
    """Abre o visualizador GUI do fotonPDF."""
    try:
        from src.interfaces.gui.app import main
        import sys
        
        # Injetar o arquivo se passado via argumento
        if path:
            sys.argv.append(str(path))
            
        click.echo("🚀 Abrindo Visualizador Fóton...")
        main()
        
    except Exception as e:
        notify_error(str(e))

@cli.command()
def setup():
    """🚀 Configura o fotonPDF no seu sistema (Menu de Contexto)."""
    from src.interfaces.cli.setup_wizard import run_setup
    run_setup()


@cli.command()
@click.option('--yes', '-y', is_flag=True, help='Pula a confirmação')
def uninstall(yes: bool):
    """🗑️ Remove o fotonPDF do sistema."""
    from src.interfaces.cli.uninstall_wizard import run_uninstall
    run_uninstall(skip_confirmation=yes)


@cli.command()
def status():
    """📊 Verifica o status da instalação do fotonPDF."""
    from src import __version__
    from src.infrastructure.adapters.windows_registry_adapter import WindowsRegistryAdapter
    
    click.echo()
    click.secho(f"fotonPDF v{__version__}", fg='cyan', bold=True)
    click.echo("─" * 40)
    
    adapter = WindowsRegistryAdapter()
    is_installed = adapter.check_installation_status()
    
    click.echo(f"Menu de Contexto: ", nl=False)
    if is_installed:
        click.secho("✅ Instalado", fg='green')
    else:
        click.secho("❌ Não instalado", fg='red')
        click.echo()
        click.secho("Dica: Execute 'foton setup' para configurar.", fg='yellow')
    
    click.echo()


if __name__ == '__main__':
    cli()
