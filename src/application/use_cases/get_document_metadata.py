from pathlib import Path
from src.domain.ports.pdf_operations import PDFOperationsPort

class GetDocumentMetadataUseCase:
    """Caso de uso para obter metadados técnicos do PDF (páginas, tamanhos)."""
    
    def __init__(self, pdf_port: PDFOperationsPort):
        self._pdf_port = pdf_port

    def execute(self, pdf_path: Path) -> dict:
        if not pdf_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {pdf_path}")
            
        return self._pdf_port.get_document_metadata(pdf_path)
