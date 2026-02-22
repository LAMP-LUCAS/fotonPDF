import sys
import os

# ─── Safe I/O Guard ───────────────────────────────────────────────────────
# Quando empacotado com PyInstaller em modo GUI (console=False), sys.stdout
# e sys.stderr são None. Isso faz click.echo e print crasharem silenciosamente.
# Redirecionamos para devnull nesses casos para evitar OSError.
if sys.stdout is None:
    sys.stdout = open(os.devnull, 'w')
if sys.stderr is None:
    sys.stderr = open(os.devnull, 'w')
# ──────────────────────────────────────────────────────────────────────────

import click
from pathlib import Path
from src.infrastructure.adapters.pymupdf_adapter import PyMuPDFAdapter
from src.infrastructure.adapters.notification_adapter import PlyerNotificationAdapter
from src.application.use_cases.rotate_pdf import RotatePDFUseCase
from src.application.use_cases.merge_pdf import MergePDFUseCase
from src.application.use_cases.split_pdf import SplitPDFUseCase
from src.application.use_cases.export_image import ExportImageUseCase
from src.application.use_cases.export_svg import ExportSVGUseCase
from src.application.use_cases.export_markdown import ExportMarkdownUseCase
from src.infrastructure.services.logger import log_info, log_error, log_debug, log_exception
from src.application.services.update_service import UpdateService

def notify_success(title: str, msg: str):
    click.secho(f"✅ {msg}", fg='green')
    log_info(f"Sucesso: {title} - {msg}")
    PlyerNotificationAdapter().notify(title, msg)

def notify_error(msg: str):
    click.secho(f"❌ Erro: {msg}", fg='red', err=True)
    log_error(f"Erro: {msg}")
    PlyerNotificationAdapter().notify("Erro no fotonPDF", msg)

@click.group()
def cli():
    """fotonPDF - O toolkit de PDFs mais rápido do mundo!"""
    pass

@cli.command()
@click.argument('path', type=click.Path(exists=True, path_type=Path))
@click.option('--degrees', '-d', type=int, default=90, help='Angulo de rotação (90, 180, 270)')
def rotate(path: Path, degrees: int):
    """Gira todas as páginas de um arquivo PDF."""
    log_info(f"Comando: rotate | Arquivo: {path} | Graus: {degrees}")
    try:
        adapter = PyMuPDFAdapter()
        use_case = RotatePDFUseCase(adapter)
        
        click.echo(f"🔄 Rotacionando {path.name} em {degrees}°...")
        output_path = use_case.execute(path, degrees)
        notify_success("Rotação Concluída", f"Arquivo salvo em: {output_path.name}")
        
    except Exception as e:
        log_exception(f"Erro no comando rotate: {e}")
        notify_error(str(e))

@cli.command()
@click.argument('paths', nargs=-1, type=click.Path(exists=True, path_type=Path), required=True)
@click.option('--output', '-o', type=click.Path(path_type=Path), help='Caminho de saída')
def merge(paths: tuple[Path, ...], output: Path | None):
    """Une múltiplos arquivos PDF em um só."""
    log_info(f"Comando: merge | Arquivos: {len(paths)}")
    try:
        if not output:
            output = paths[0].parent / "merged.pdf"
            
        adapter = PyMuPDFAdapter()
        use_case = MergePDFUseCase(adapter)
        
        click.echo(f"📑 Unindo {len(paths)} arquivos...")
        output_path = use_case.execute(list(paths), output)
        notify_success("União Concluída", f"Arquivo unido: {output_path.name}")
        
    except Exception as e:
        log_exception(f"Erro no comando merge: {e}")
        notify_error(str(e))

@cli.command()
@click.argument('path', type=click.Path(exists=True, path_type=Path))
@click.option('--pages', '-p', required=True, help='Páginas para extrair (ex: 1,2,5-8)')
@click.option('--output', '-o', type=click.Path(path_type=Path), help='Caminho de saída')
def split(path: Path, pages: str, output: Path | None):
    """Extrai páginas específicas de um PDF."""
    log_info(f"Comando: split | Arquivo: {path} | Páginas: {pages}")
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
        log_exception(f"Erro no comando split: {e}")
        notify_error(str(e))

@cli.command(name="export-img")
@click.argument('path', type=click.Path(exists=True, path_type=Path))
@click.option('--page', '-p', type=int, default=None, help='Página (0-based) ou omitir para todas')
@click.option('--fmt', '-f', type=click.Choice(['png', 'jpg', 'webp']), default='png')
def export_img(path: Path, page: int | None, fmt: str):
    """Exporta página(s) para imagem (High-DPI)."""
    log_info(f"Comando: export-img | Arquivo: {path} | Página: {page} | Formato: {fmt}")
    try:
        adapter = PyMuPDFAdapter()
        use_case = ExportImageUseCase(adapter)
        
        click.echo(f"🚀 Exportando {'todas as páginas' if page is None else f'página {page+1}'}...")
        outputs = use_case.execute(path, page, path.parent, fmt=fmt)
        
        msg = f"{len(outputs)} imagens salvas em: {path.parent.name}"
        notify_success("Exportação de Imagem", msg)
    except Exception as e:
        log_exception(f"Erro no comando export-img: {e}")
        notify_error(str(e))

@cli.command(name="export-svg")
@click.argument('path', type=click.Path(exists=True, path_type=Path))
@click.option('--page', '-p', type=int, default=None, help='Página (0-based) ou omitir para todas')
def export_svg(path: Path, page: int | None):
    """Exporta página(s) específica para SVG."""
    log_info(f"Comando: export-svg | Arquivo: {path} | Página: {page}")
    try:
        adapter = PyMuPDFAdapter()
        use_case = ExportSVGUseCase(adapter)
        
        click.echo(f"🚀 Exportando {'todas as páginas' if page is None else f'página {page+1}'}...")
        outputs = use_case.execute(path, page, path.parent)
        
        msg = f"{len(outputs)} SVGs salvos em: {path.parent.name}"
        notify_success("Exportação SVG", msg)
    except Exception as e:
        log_exception(f"Erro no comando export-svg: {e}")
        notify_error(str(e))

@cli.command(name="export-md")
@click.argument('path', type=click.Path(exists=True, path_type=Path))
def export_md(path: Path):
    """Exporta o conteúdo do PDF como Markdown."""
    log_info(f"Comando: export-md | Arquivo: {path}")
    try:
        adapter = PyMuPDFAdapter()
        use_case = ExportMarkdownUseCase(adapter)
        output = path.parent / f"{path.stem}.md"
        use_case.execute(path, output)
        notify_success("Exportação Markdown", f"Markdown salvo em: {output.name}")
    except Exception as e:
        log_exception(f"Erro no comando export-md: {e}")
        notify_error(str(e))

@cli.command()
@click.argument('path', type=click.Path(exists=True, path_type=Path), required=False)
def view(path: Path | None):
    """Abre o visualizador GUI do fotonPDF."""
    log_info(f"Comando: view | Arquivo: {path}")
    try:
        from src.interfaces.gui.app import main
        
        click.echo("  [OK] Abrindo Visualizador...")
        main(file_path=str(path) if path else None)
        
    except Exception as e:
        log_exception(f"Erro no comando view: {e}")
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


@cli.command()
def update():
    """🚀 Verifica se há uma nova versão do fotonPDF disponível."""
    click.echo("🔍 Verificando atualizações...")
    service = UpdateService()
    new_version = service.check_for_updates()
    
    if new_version:
        click.secho(f"\n🎉 Uma nova versão está disponível: v{new_version['version']}", fg='green', bold=True)
        click.echo(f"🔗 Link: {new_version['url']}")
        click.echo("\nNotas da Versão:")
        click.echo(new_version['body'])
        click.echo("-" * 40)
        click.secho("\nPara atualizar, baixe a nova versão no link acima.", fg='yellow')
    else:
        click.secho("\n✅ Você já está usando a versão mais recente!", fg='cyan')
    click.echo()



if __name__ == '__main__':
    import sys
    import os
    
    # Verifica se há console/stdin válido (importante para build windowed)
    has_console = sys.stdin is not None and sys.stdin.isatty()
    
    # Se executado sem argumentos (clique duplo)
    if len(sys.argv) == 1:
        if not has_console:
            # Em modo windowed (sem terminal), prioridade total à GUI
            from src.interfaces.gui.app import main
            main()
        else:
            # Em um terminal real, abrir menu interativo (UX Legada)
            try:
                from src.interfaces.cli.interactive_menu import run_interactive_menu
                run_interactive_menu()
            except RuntimeError:
                # Fallback de segurança: se o menu CLI falhar por I/O, abre a GUI
                from src.interfaces.gui.app import main
                main()
    else:
        # Com argumentos, segue para o CLI normal (click handles everything)
        cli()
