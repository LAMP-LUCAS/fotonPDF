from pathlib import Path
from src.domain.ports.pdf_operations import PDFOperationsPort

class ExportImageUseCase:
    """Caso de uso para exportar uma página de um PDF como imagem."""

    def __init__(self, pdf_ops: PDFOperationsPort):
        self._pdf_ops = pdf_ops

    def execute(self, pdf_path: Path, page_index: int | None, output_dir: Path, fmt: str = "png", dpi: int = 300) -> list[Path]:
        """
        Executa a exportação de página(s) para imagem.
        
        Args:
            pdf_path: Caminho do PDF original.
            page_index: Índice da página (0-based) ou None para todas.
            output_dir: Diretório onde as imagens serão salvas.
            fmt: Formato da imagem (png, jpg, webp).
            dpi: Resolução da imagem.
            
        Returns:
            list[Path]: Lista de caminhos dos arquivos gerados.
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {pdf_path}")
            
        return self._pdf_ops.export_page_to_image(pdf_path, page_index, output_dir, fmt, dpi)
