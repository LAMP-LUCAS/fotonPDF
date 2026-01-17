import fitz  # PyMuPDF
from pathlib import Path
from datetime import datetime
from src.domain.entities.pdf import PDFDocument
from src.domain.ports.pdf_operations import PDFOperationsPort

class PyMuPDFAdapter(PDFOperationsPort):
    """Implementação concreta (Adapter) usando a biblioteca PyMuPDF."""

    def _get_timestamp(self) -> str:
        """Retorna timestamp formatado para nome de arquivo."""
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def rotate(self, pdf: PDFDocument, degrees: int) -> Path:
        """Rotaciona o PDF usando PyMuPDF."""
        doc = fitz.open(str(pdf.path))
        
        for page in doc:
            new_rotation = (page.rotation + degrees) % 360
            page.set_rotation(new_rotation)
        
        # Nome com timestamp para evitar sobrescritas
        timestamp = self._get_timestamp()
        output_path = pdf.path.with_name(f"{pdf.path.stem}_rotated_{timestamp}{pdf.path.suffix}")
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
        
        # Adicionar timestamp se o caminho não foi especificado pelo usuário
        if output_path.name == "merged.pdf":
            timestamp = self._get_timestamp()
            output_path = output_path.with_name(f"merged_{timestamp}.pdf")
                
        result.save(str(output_path))
        result.close()
        return output_path

    def split(self, pdf: PDFDocument, pages: list[int], output_path: Path) -> Path:
        """Extrai páginas específicas usando PyMuPDF."""
        with fitz.open(str(pdf.path)) as src:
            src.select(pages)
            
            # Nome com timestamp para evitar sobrescritas
            timestamp = self._get_timestamp()
            final_output = output_path.with_name(f"{output_path.stem}_{timestamp}{output_path.suffix}")
            src.save(str(final_output))
            
        return final_output
