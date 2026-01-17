from abc import ABC, abstractmethod
from pathlib import Path
from src.domain.entities.pdf import PDFDocument

class PDFOperationsPort(ABC):
    """Porta (Interface) para operações técnicas em arquivos PDF."""

    @abstractmethod
    def rotate(self, pdf: PDFDocument, degrees: int) -> Path:
        """Rotaciona todas as páginas do PDF pelos graus informados."""
        pass

    @abstractmethod
    def get_info(self, path: Path) -> PDFDocument:
        """Extrai metadados básicos do PDF."""
        pass
