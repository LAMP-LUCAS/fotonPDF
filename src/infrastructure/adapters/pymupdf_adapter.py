import fitz  # PyMuPDF
from pathlib import Path
from src.domain.entities.pdf import PDFDocument
from src.domain.ports.pdf_operations import PDFOperationsPort
from src.domain.services.naming_service import NamingService

class PyMuPDFAdapter(PDFOperationsPort):
    """Implementação concreta (Adapter) usando a biblioteca PyMuPDF."""

    def rotate(self, pdf: PDFDocument, degrees: int) -> Path:
        """Rotaciona o PDF usando PyMuPDF."""
        doc = fitz.open(str(pdf.path))
        
        for page in doc:
            new_rotation = (page.rotation + degrees) % 360
            page.set_rotation(new_rotation)
        
        output_path = NamingService.generate_output_path(
            pdf.path, 
            pdf.path.parent, 
            tag="rotated", 
            suffix=pdf.path.suffix
        )
        
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
        
        # Se for o default 'merged.pdf', regeneramos seguindo a lógica centralizada
        if output_path.name == "merged.pdf":
            output_path = NamingService.generate_output_path(
                output_path, 
                output_path.parent, 
                suffix=".pdf"
            )
        else:
            # Garante o timestamp mesmo em nomes customizados para segurança/unicidade
            output_path = NamingService.generate_output_path(
                output_path, 
                output_path.parent, 
                suffix=output_path.suffix
            )
                
        result.save(str(output_path))
        result.close()
        return output_path

    def split(self, pdf: PDFDocument, pages: list[int], output_path: Path) -> Path:
        """Extrai páginas específicas usando PyMuPDF."""
        with fitz.open(str(pdf.path)) as src:
            src.select(pages)
            
            final_output = NamingService.generate_output_path(
                pdf.path, 
                output_path, 
                tag="split", 
                suffix=pdf.path.suffix
            )
            src.save(str(final_output))
            
        return final_output

    def export_page_to_image(self, pdf_path: Path, page_index: int | None, output_dir: Path, fmt: str = "png", dpi: int = 300) -> list[Path]:
        """Exporta página(s) para imagem usando PyMuPDF."""
        exported = []
        with fitz.open(str(pdf_path)) as doc:
            indices = [page_index] if page_index is not None else range(len(doc))
            total_pages = len(doc)
            
            for idx in indices:
                page = doc[idx]
                zoom = dpi / 72
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat, alpha=False)
                
                final_path = NamingService.generate_output_path(
                    pdf_path, 
                    output_dir, 
                    page_index=idx if page_index is None or total_pages > 1 else None,
                    total_pages=total_pages,
                    suffix=f".{fmt}"
                )
                
                pix.save(str(final_path))
                exported.append(final_path)
        return exported

    def export_page_to_svg(self, pdf_path: Path, page_index: int | None, output_dir: Path) -> list[Path]:
        """Exporta página(s) para SVG usando PyMuPDF."""
        exported = []
        with fitz.open(str(pdf_path)) as doc:
            indices = [page_index] if page_index is not None else range(len(doc))
            total_pages = len(doc)
            
            for idx in indices:
                page = doc[idx]
                svg = page.get_svg_image()
                
                final_path = NamingService.generate_output_path(
                    pdf_path, 
                    output_dir, 
                    page_index=idx if page_index is None or total_pages > 1 else None,
                    total_pages=total_pages,
                    suffix=".svg"
                )
                
                final_path.write_text(svg, encoding="utf-8")
                exported.append(final_path)
        return exported

    def export_to_markdown(self, pdf_path: Path, output_path: Path) -> Path:
        """Extrai texto estruturado para Markdown usando PyMuPDF."""
        with fitz.open(str(pdf_path)) as doc:
            full_text = ""
            for i, page in enumerate(doc):
                full_text += f"# Página {i+1}\n\n"
                try:
                    content = page.get_text("markdown")
                except:
                    content = page.get_text("text")
                full_text += content + "\n\n---\n\n"
            
            final_output = NamingService.generate_output_path(
                pdf_path, 
                output_path, 
                suffix=".md"
            )
                
            final_output.write_text(full_text, encoding="utf-8")
        return final_output
