from pathlib import Path
from src.domain.ports.pdf_operations import PDFOperationsPort

class AddAnnotationUseCase:
    """Caso de uso para adicionar anotações (realces, etc.) ao PDF."""
    
    def __init__(self, pdf_port: PDFOperationsPort):
        self._pdf_port = pdf_port

    def execute(self, pdf_path: Path, page_index: int, rect: tuple, type: str = "highlight", color: tuple = (1, 1, 0)) -> Path:
        if not pdf_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {pdf_path}")
            
        return self._pdf_port.add_annotation(
            pdf_path, 
            page_index, 
            rect, 
            type=type, 
            color=color
        )
