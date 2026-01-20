from pathlib import Path
from src.domain.ports.ocr_operations import OCRPort

class ApplyOCRUseCase:
    """Caso de uso para tornar um PDF pesquisável via OCR."""

    def __init__(self, ocr_port: OCRPort):
        self._ocr_port = ocr_port

    def execute(self, pdf_path: Path, output_path: Path = None) -> Path:
        """Executa o OCR e retorna o caminho do novo arquivo."""
        if not pdf_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {pdf_path}")
            
        if not self._ocr_port.is_engine_available():
            raise RuntimeError("Motor de OCR não disponível. Verifique se o Tesseract está instalado.")

        return self._ocr_port.apply_ocr(pdf_path, output_path)
