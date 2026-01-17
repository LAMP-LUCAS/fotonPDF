import fitz  # PyMuPDF
from pathlib import Path
from src.domain.entities.pdf import PDFDocument
from src.domain.ports.pdf_operations import PDFOperationsPort

class PyMuPDFAdapter(PDFOperationsPort):
    """Implementação concreta (Adapter) usando a biblioteca PyMuPDF."""

    def rotate(self, pdf: PDFDocument, degrees: int) -> Path:
        """Rotaciona o PDF usando PyMuPDF."""
        doc = fitz.open(str(pdf.path))
        
        for page in doc:
            # fitz usa graus absolutos ou relativos (set_rotation vs rotation)
            # Aqui adicionamos à rotação atual
            new_rotation = (page.rotation + degrees) % 360
            page.set_rotation(new_rotation)
            
        output_path = pdf.path.with_name(f"{pdf.path.stem}_rotated{pdf.path.suffix}")
        doc.save(str(output_path))
        doc.close()
        
        return output_path

    def get_info(self, path: Path) -> PDFDocument:
        """Obtém metadados via PyMuPDF."""
        doc = fitz.open(str(path))
        page_count = doc.page_count
        doc.close()
        
        return PDFDocument(
            path=path,
            name=path.name,
            page_count=page_count
        )

    def merge(self, documents: list[PDFDocument], output_path: Path) -> Path:
        """Une múltiplos documentos PDF usando PyMuPDF."""
        result = fitz.open()
        
        for pdf in documents:
            with fitz.open(str(pdf.path)) as src:
                result.insert_pdf(src)
                
        result.save(str(output_path))
        result.close()
        return output_path

    def split(self, pdf: PDFDocument, pages: list[int], output_path: Path) -> Path:
        """Extrai páginas específicas usando PyMuPDF."""
        with fitz.open(str(pdf.path)) as src:
            # O método select() modifica o documento in-place (na memória)
            # para conter apenas as páginas especificadas
            src.select(pages)
            src.save(str(output_path))
            
        return output_path
