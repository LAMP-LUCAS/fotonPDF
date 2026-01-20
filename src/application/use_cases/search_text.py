from pathlib import Path
from src.domain.ports.pdf_operations import PDFOperationsPort

class SearchTextUseCase:
    """Caso de uso para buscar texto em um documento PDF."""

    def __init__(self, pdf_ops: PDFOperationsPort):
        self._pdf_ops = pdf_ops

    def execute(self, pdf_path: Path, query: str) -> list:
        """
        Executa a busca e retorna uma lista de SearchResult.
        
        Args:
            pdf_path: Caminho do PDF.
            query: Termo de busca.
            
        Returns:
            list[SearchResult]: Resultados encontrados.
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {pdf_path}")
            
        if not query or len(query.strip()) < 2:
            return []

        return self._pdf_ops.search_text(pdf_path, query)
