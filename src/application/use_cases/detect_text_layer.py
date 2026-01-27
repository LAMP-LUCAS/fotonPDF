from pathlib import Path
from src.domain.ports.ocr_operations import OCRPort

class DetectTextLayerUseCase:
    """Caso de uso para identificar se um PDF precisa de OCR."""

    def __init__(self, ocr_port: OCRPort):
        self._ocr_port = ocr_port

    def execute(self, pdf_path: Path, doc_handle=None) -> bool:
        """Retorna True se o documento POSSUI camada de texto."""
        if not pdf_path.exists():
            return False
        return self._ocr_port.has_text_layer(pdf_path, doc_handle=doc_handle)
