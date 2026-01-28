import fitz  # PyMuPDF
from pathlib import Path
from typing import Tuple
from src.domain.entities.pdf import PDFDocument
from src.domain.ports.pdf_operations import PDFOperationsPort
from src.domain.ports.ocr_operations import OCRPort
from src.domain.services.naming_service import NamingService

class PyMuPDFAdapter(PDFOperationsPort, OCRPort):
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

    def search_text(self, pdf_path: Path, query: str) -> list:
        """Busca textual com localização e extração de contexto via PyMuPDF."""
        from src.domain.entities.navigation import SearchResult
        results = []
        
        with fitz.open(str(pdf_path)) as doc:
            for i, page in enumerate(doc):
                # Busca por ocorrências (usando quadras para precisão visual)
                hits = page.search_for(query)
                if hits:
                    # Tenta extrair um pequeno contexto ao redor do primeiro hit da página
                    # para mostrar no painel lateral.
                    text = page.get_text("text")
                    start_idx = text.lower().find(query.lower())
                    snippet = text[max(0, start_idx-30):min(len(text), start_idx+len(query)+30)]
                    snippet = snippet.replace("\n", " ").strip()
                    if start_idx > 30: snippet = "..." + snippet
                    if start_idx + len(query) + 30 < len(text): snippet = snippet + "..."

                    results.append(SearchResult(
                        page_index=i,
                        text_snippet=snippet,
                        highlights=[(h.x0, h.y0, h.x1, h.y1) for h in hits]
                    ))
        return results

    def get_toc(self, pdf_path: Path) -> list:
        """Retorna a árvore de sumário formatada."""
        from src.domain.entities.navigation import TOCItem
        
        with fitz.open(str(pdf_path)) as doc:
            toc_data = doc.get_toc() # [level, title, page, ...]
            # PyMuPDF TOC page is 1-based, converting to 0-based for standard
            return [TOCItem(level=item[0], title=item[1], page_index=item[2]-1) for item in toc_data]

    def add_annotation(self, pdf_path: Path, page_index: int, rect: tuple, type: str = "highlight", color: tuple = (1, 1, 0)) -> Path:
        """Adiciona uma anotação em uma área específica e salva o arquivo modificado."""
        doc = fitz.open(str(pdf_path))
        page = doc.load_page(page_index)
        
        # Converte a tupla (x0, y0, x1, y1) para fitz.Rect
        fitz_rect = fitz.Rect(rect)
        
        if type == "highlight":
            annot = page.add_highlight_annot(fitz_rect)
        elif type == "underline":
            annot = page.add_underline_annot(fitz_rect)
        else:
            annot = page.add_rect_annot(fitz_rect)
            
        annot.set_colors(stroke=color)
        annot.update()
        
        # Salva em um arquivo temporário seguindo a política de nomes
        output_path = NamingService.generate_output_path(
            pdf_path, 
            pdf_path.parent, 
            suffix=f"_{type}.pdf"
        )
        
        doc.save(str(output_path))
        doc.close()
        return output_path

    def get_document_metadata(self, pdf_path: Path, doc_handle=None) -> dict:
        """Extrai metadados técnicos (páginas, dimensões e formato AEC) via PyMuPDF."""
        from src.domain.services.geometry_service import GeometryService
        
        metadata = {
            "page_count": 0,
            "pages": [], # list of {width, height, format}
            "layers": self.get_layers(pdf_path, doc_handle=doc_handle)
        }
        
        # Se handle não fornecido, abre e garante fechamento
        doc = doc_handle if doc_handle else fitz.open(str(pdf_path))
        try:
            metadata["page_count"] = doc.page_count
            for page in doc:
                rect = page.rect
                fmt = GeometryService.identify_aec_format(rect.width, rect.height)
                metadata["pages"].append({
                    "width_pt": rect.width,
                    "height_pt": rect.height,
                    "width_mm": GeometryService.points_to_mm(rect.width),
                    "height_mm": GeometryService.points_to_mm(rect.height),
                    "format": fmt
                })
        finally:
            if not doc_handle: 
                doc.close()
                
        return metadata

    def get_layers(self, pdf_path: Path, doc_handle=None) -> list[dict]:
        """Extrai grupos de conteúdo opcional (OCG/Layers) usando PyMuPDF."""
        doc = doc_handle if doc_handle else fitz.open(str(pdf_path))
        try:
            ocgs = doc.get_ocgs()
            return [{"id": ocg_id, "name": config["name"], "visible": config["on"]} 
                    for ocg_id, config in ocgs.items()]
        finally:
            if not doc_handle:
                doc.close()

    def set_layer_visibility(self, pdf_path: Path, layer_id: int, visible: bool) -> None:
        """Altera a visibilidade de uma camada diretamente no documento."""
        with fitz.open(str(pdf_path)) as doc:
            doc.set_ocg(layer_id, on=visible)
            doc.saveIncremental()

    def render_page(self, pdf_path: Path, page_index: int, zoom: float, rotation: int, clip: tuple | None = None, doc_handle=None) -> tuple:
        """
        Renderiza uma página e retorna (bytes, width, height, stride).
        Suporta 'clip' (x0, y0, x1, y1) para renderização parcial (Tiling).
        Otimizado: Suporta reutilização de handle (Single-Open).
        """
        doc = doc_handle if doc_handle else fitz.open(str(pdf_path))
        try:
            page = doc.load_page(page_index)
            mat = fitz.Matrix(zoom, zoom)
            if rotation != 0:
                mat.prerotate(rotation)
            
            fitz_clip = fitz.Rect(clip) if clip else None
            pix = page.get_pixmap(matrix=mat, alpha=False, clip=fitz_clip)
            return (pix.samples, pix.width, pix.height, pix.stride)
        finally:
            if not doc_handle:
                doc.close()

    def has_text_layer(self, pdf_path: Path, doc_handle=None) -> bool:
        """
        Verifica se o PDF tem camada de texto (Pesquisabilidade).
        Otimizado: Amostragem 'Lazy' interrompe assim que detecta densidade.
        """
        doc = doc_handle if doc_handle else fitz.open(str(pdf_path))
        try:
            total_text_len = 0
            # Amostra das primeiras 5 páginas
            pages_to_check = doc[:min(5, len(doc))]
            for page in pages_to_check:
                text = page.get_text("text").strip()
                total_text_len += len(text)
                
                # Otimização: Se a página já tem bastante texto, não precisa checar o resto
                if len(text) > 100: 
                    return True
            
            avg_text = total_text_len / len(pages_to_check) if pages_to_check else 0
            return avg_text > 50
        finally:
            if not doc_handle:
                doc.close()

    def is_engine_available(self) -> bool:
        """Verifica se o Tesseract está disponível para o PyMuPDF."""
        try:
            # Tenta um OCR simples em uma página vazia para testar o binário
            import shutil
            # Se 'tesseract' estiver no PATH, o PyMuPDF costuma encontrá-lo
            has_binary = shutil.which("tesseract") is not None
            return has_binary
        except:
            return False

    def apply_ocr(self, pdf_path: Path, output_path: Path, language: str = "por+eng") -> Path:
        """
        Gera uma versão pesquisável do PDF.
        Nota: PyMuPDF usa 'pdfocr_save' ou OCR via renderização.
        """
        if not self.is_engine_available():
            raise RuntimeError("Motor Tesseract não encontrado no sistema.")

        # Gerar nome de saída caso não provido
        if not output_path or output_path == pdf_path:
            output_path = NamingService.generate_output_path(
                pdf_path, 
                pdf_path.parent, 
                tag="ocr", 
                suffix=".pdf"
            )

        with fitz.open(str(pdf_path)) as doc:
            # OCR em cada página e salva como novo PDF
            # O PyMuPDF possui integração direta através do método 'pdfocr_save'
            # (Requer fitz[ocr] ou tesseract instalado)
            doc.pdfocr_save(str(output_path), language=language, treadmill=True)
            
        return output_path

    def extract_text_from_area(self, pdf_path: Path, page_index: int, area: Tuple[float, float, float, float], language: str = "por+eng") -> str:
        """Extrai texto de uma região específica usando OCR on-demand."""
        if not self.is_engine_available():
            raise RuntimeError("Motor Tesseract não encontrado no sistema.")

        with fitz.open(str(pdf_path)) as doc:
            page = doc[page_index]
            # Converte Tupla (x0, y0, x1, y1) para Rect
            rect = fitz.Rect(area)
            # Tenta extrair texto via OCR apenas daquela área
            return page.get_textbox(rect, method="ocr", language=language)

    def get_text_in_rect(self, pdf_path: Path | str, page_index: int, rect: Tuple[float, float, float, float]) -> str:
        """
        Extrai texto de uma área específica SEM usar OCR.
        Ideal para PDFs com camada de texto existente.
        """
        try:
            pdf_path_str = str(pdf_path) if isinstance(pdf_path, Path) else pdf_path
            with fitz.open(pdf_path_str) as doc:
                if page_index < 0 or page_index >= len(doc):
                    return ""
                page = doc[page_index]
                # Converte Tupla (x0, y0, x1, y1) para Rect
                area = fitz.Rect(rect)
                # Extrai texto da área usando a camada de texto existente
                return page.get_textbox(area)
        except Exception:
            return ""
    @staticmethod
    def get_text(path: str, page_index: int, option: str = "text"):
        """
        Extrai texto ou estrutura de uma página de forma estática.
        option: "text", "blocks", "words", "html", etc.
        """
        try:
            doc = fitz.open(str(path))
            # Validação básica
            if page_index < 0 or page_index >= doc.page_count:
                return None
            
            page = doc[page_index]
            result = page.get_text(option)
            doc.close()
            return result
        except Exception as e:
            print(f"Error extracting text from {path}: {e}")
            return None
