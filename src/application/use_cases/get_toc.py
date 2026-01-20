from pathlib import Path
from src.domain.ports.pdf_operations import PDFOperationsPort

class GetTOCUseCase:
    """Caso de uso para extrair o sumário (Bookmarks) de um PDF."""

    def __init__(self, pdf_ops: PDFOperationsPort):
        self._pdf_ops = pdf_ops

    def execute(self, pdf_path: Path) -> list:
        """
        Retorna a lista de itens do sumário (TOCItem).
        
        Args:
            pdf_path: Caminho do PDF.
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {pdf_path}")

        return self._pdf_ops.get_toc(pdf_path)
