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
def install():
    """Registra o fotonPDF no Menu de Contexto (Windows)."""
    try:
        from src.application.use_cases.register_os import RegisterOSIntegrationUseCase
        from src.infrastructure.adapters.windows_registry_adapter import WindowsRegistryAdapter
        import sys
        
        # Detectar caminho do executável ou script
        if getattr(sys, 'frozen', False):
            app_path = Path(sys.executable)
            command = f'"{app_path}" view "%1"'
        else:
            app_path = Path(sys.argv[0]).absolute()
            command = f'python "{app_path}" view "%1"'
            
        adapter = WindowsRegistryAdapter()
        use_case = RegisterOSIntegrationUseCase(adapter)
        
        click.echo(f"🪟 Registrando no Windows Explorer: {app_path.name}")
        
        if use_case.execute("Abrir com fotonPDF", command):
            notify_success("Instalação Concluída", "fotonPDF registrado no Menu de Contexto!")
        else:
            notify_error("Falha ao registrar no Windows. Tente como Admin.")
            
    except Exception as e:
        notify_error(str(e))

@cli.command()
def remove():
    """Remove o fotonPDF do Menu de Contexto (Windows)."""
    try:
        from src.application.use_cases.unregister_os import UnregisterOSIntegrationUseCase
        from src.infrastructure.adapters.windows_registry_adapter import WindowsRegistryAdapter
        
        adapter = WindowsRegistryAdapter()
        use_case = UnregisterOSIntegrationUseCase(adapter)
        
        click.echo("🧹 Removendo do Windows Explorer...")
        if use_case.execute():
            notify_success("Remoção Concluída", "fotonPDF removido do Menu de Contexto!")
        else:
            notify_error("Falha ao remover do Windows. Tente como Admin.")
            
    except Exception as e:
        notify_error(str(e))

if __name__ == '__main__':
    cli()
