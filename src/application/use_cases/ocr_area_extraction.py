from pathlib import Path
from typing import Tuple
from src.domain.ports.ocr_operations import OCRPort

class OCRAreaExtractionUseCase:
    """Caso de uso para extrair texto de uma região da página via OCR."""

    def __init__(self, ocr_port: OCRPort):
        self._ocr_port = ocr_port

    def execute(self, pdf_path: Path, page_index: int, area: Tuple[float, float, float, float]) -> str:
        """Retorna o texto reconhecido na área selecionada."""
        if not pdf_path.exists():
            return ""
            
        if not self._ocr_port.is_engine_available():
            return "ERRO: Motor OCR não disponível."

        return self._ocr_port.extract_text_from_area(pdf_path, page_index, area)
