from abc import ABC, abstractmethod
from pathlib import Path
from typing import Tuple

class OCRPort(ABC):
    """Porta para operações de reconhecimento óptico de caracteres (OCR)."""

    @abstractmethod
    def has_text_layer(self, pdf_path: Path) -> bool:
        """Verifica se o PDF possui camada de texto significativa."""
        pass

    @abstractmethod
    def apply_ocr(self, pdf_path: Path, output_path: Path, language: str = "por+eng") -> Path:
        """Aplica OCR ao documento inteiro e gera um novo PDF pesquisável."""
        pass

    @abstractmethod
    def extract_text_from_area(self, pdf_path: Path, page_index: int, area: Tuple[float, float, float, float], language: str = "por+eng") -> str:
        """Extrai texto de uma área específica da página usando OCR."""
        pass

    @abstractmethod
    def is_engine_available(self) -> bool:
        """Verifica se o motor de OCR (ex: Tesseract) está instalado e configurado."""
        pass
