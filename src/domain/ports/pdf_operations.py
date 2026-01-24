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

    @abstractmethod
    def merge(self, documents: list[PDFDocument], output_path: Path) -> Path:
        """Une múltiplos documentos PDF em um único arquivo."""
        pass

    @abstractmethod
    def split(self, pdf: PDFDocument, pages: list[int], output_path: Path) -> Path:
        """Extrai páginas específicas de um PDF para um novo arquivo."""
        pass

    @abstractmethod
    def export_page_to_image(self, pdf_path: Path, page_index: int | None, output_dir: Path, fmt: str = "png", dpi: int = 300) -> list[Path]:
        """
        Exporta página(s) para imagem. 
        Se page_index for None, exporta todas.
        """
        pass

    @abstractmethod
    def export_page_to_svg(self, pdf_path: Path, page_index: int | None, output_dir: Path) -> list[Path]:
        """
        Exporta página(s) para SVG. 
        Se page_index for None, exporta todas.
        """
        pass

    @abstractmethod
    def export_to_markdown(self, pdf_path: Path, output_path: Path) -> Path:
        """Exporta o conteúdo textual do documento para Markdown."""
        pass

    @abstractmethod
    def search_text(self, pdf_path: Path, query: str) -> list:
        """Busca texto em todas as páginas do PDF."""
        pass

    @abstractmethod
    def get_toc(self, pdf_path: Path) -> list:
        """Extrai o sumário (bookmarks) do PDF."""
        pass

    @abstractmethod
    def add_annotation(self, pdf_path: Path, page_index: int, rect: tuple, type: str = "highlight", color: tuple = (1, 1, 0)) -> Path:
        """Adiciona uma anotação (realce/sublinhado) em uma área específica e salva."""
        pass

    @abstractmethod
    def get_document_metadata(self, pdf_path: Path) -> dict:
        """Retorna metadados técnicos do documento (número de páginas, dimensões das páginas, etc.)."""
        pass

    @abstractmethod
    def render_page(self, pdf_path: Path, page_index: int, zoom: float, rotation: int) -> tuple:
        """Renderiza uma página e retorna (bytes, width, height, stride)."""
        pass

    @abstractmethod
    def get_layers(self, pdf_path: Path) -> list[dict]:
        """Retorna a lista de camadas (OCG) do documento."""
        pass

    @abstractmethod
    def set_layer_visibility(self, pdf_path: Path, layer_id: int, visible: bool) -> None:
        """Altera a visibilidade de uma camada específica."""
        pass
