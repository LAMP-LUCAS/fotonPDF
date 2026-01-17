from pathlib import Path
from typing import List
from src.domain.entities.pdf import PDFDocument
from src.domain.ports.pdf_operations import PDFOperationsPort

class SplitPDFUseCase:
    """Caso de uso para extrair páginas específicas de um PDF."""

    def __init__(self, pdf_ops: PDFOperationsPort):
        self._pdf_ops = pdf_ops

    def execute(self, input_path: Path, pages: List[int], output_path: Path) -> Path:
        """
        Extrai as páginas informadas para um novo arquivo.
        
        Args:
            input_path: Caminho do PDF original.
            pages: Lista de páginas (1-based) a extrair.
            output_path: Caminho de destino.
            
        Returns:
            Path: Caminho do arquivo gerado.
        """
        if not input_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {input_path}")
            
        if not pages:
            raise ValueError("A lista de páginas não pode estar vazia.")

        pdf = self._pdf_ops.get_info(input_path)
        
        # Validar páginas
        if any(p < 1 or (pdf.page_count and p > pdf.page_count) for p in pages):
            raise ValueError(f"Uma ou mais páginas informadas são inválidas para o documento (Total: {pdf.page_count})")

        # Converter para 0-based para a porta/adaptador
        zero_based_pages = [p - 1 for p in pages]
        
        return self._pdf_ops.split(pdf, zero_based_pages, output_path)
