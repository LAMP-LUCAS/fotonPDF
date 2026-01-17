import click
from pathlib import Path
from src.application.use_cases.rotate_pdf import RotatePDFUseCase
from src.infrastructure.adapters.pymupdf_adapter import PyMuPDFAdapter

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
        click.secho(f"✅ Sucesso! Arquivo salvo em: {output_path}", fg='green')
        
    except Exception as e:
        click.secho(f"❌ Erro: {str(e)}", fg='red', err=True)

if __name__ == '__main__':
    cli()
