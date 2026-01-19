from pathlib import Path
from src.domain.ports.pdf_operations import PDFOperationsPort

class ExportSVGUseCase:
    """Caso de uso para exportar uma página de um PDF como SVG."""

    def __init__(self, pdf_ops: PDFOperationsPort):
        self._pdf_ops = pdf_ops

    def execute(self, pdf_path: Path, page_index: int | None, output_dir: Path) -> list[Path]:
        """
        Executa a exportação de página(s) para SVG.
        
        Args:
            pdf_path: Caminho do PDF original.
            page_index: Índice da página (0-based) ou None para todas.
            output_dir: Diretório onde os SVGs serão salvos.
            
        Returns:
            list[Path]: Lista de caminhos dos arquivos SVG gerados.
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {pdf_path}")
            
        return self._pdf_ops.export_page_to_svg(pdf_path, page_index, output_dir)
