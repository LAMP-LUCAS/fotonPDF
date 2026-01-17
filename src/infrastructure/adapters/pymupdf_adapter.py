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
