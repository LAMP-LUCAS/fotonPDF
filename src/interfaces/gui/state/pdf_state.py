from dataclasses import dataclass
import fitz
from typing import List, Optional

@dataclass
class VirtualPage:
    source_doc: fitz.Document
    source_page_index: int
    rotation_offset: int = 0
    
    @property
    def absolute_rotation(self) -> int:
        """Retorna a rotação absoluta (Original + Offset)."""
        original_rot = self.source_doc[self.source_page_index].rotation
        return (original_rot + self.rotation_offset) % 360

from src.infrastructure.services.logger import log_debug, log_error

class PDFStateManager:
    """Gerencia o estado virtual do documento PDF (páginas, ordem, rotação)."""
    
    def __init__(self):
        self.pages: List[VirtualPage] = []
        self._docs_keep_alive: List[fitz.Document] = [] # Evitar garbage collection

    def load_base_document(self, path: str):
        """Carrega o documento inicial, resetando o estado."""
        self.close_all()
        log_debug(f"StateManager: Carregando base {path}")
        doc = fitz.open(path)
        self._docs_keep_alive.append(doc)
        
        self.pages = [
            VirtualPage(source_doc=doc, source_page_index=i) 
            for i in range(len(doc))
        ]
        log_debug(f"StateManager: Base carregada com {len(self.pages)} páginas.")

    def append_document(self, path: str):
        """Adiciona páginas de outro documento ao final."""
        log_debug(f"StateManager: Anexando {path}")
        doc = fitz.open(path)
        self._docs_keep_alive.append(doc)
        
        new_pages = [
            VirtualPage(source_doc=doc, source_page_index=i) 
            for i in range(len(doc))
        ]
        self.pages.extend(new_pages)
        log_debug(f"StateManager: Anexado! Total agora: {len(self.pages)} páginas.")

    def rotate_page(self, global_index: int, degrees: int):
        """Aplica rotação a uma página específica."""
        if 0 <= global_index < len(self.pages):
            self.pages[global_index].rotation_offset = (self.pages[global_index].rotation_offset + degrees) % 360

    def reorder_pages(self, new_order: List[int]):
        """Reordena as páginas com base numa lista de índices."""
        if len(new_order) != len(self.pages):
           log_error(f"StateManager: Erro reorder. Esperado {len(self.pages)}, recebido {len(new_order)}")
           return # Erro de consistência
            
        self.pages = [self.pages[i] for i in new_order]

    def save(self, path: str, indices: List[int] = None):
        """Compila e salva o estado atual (ou subconjunto) em um novo arquivo."""
        target_pages = self.pages
        if indices is not None:
            target_pages = [self.pages[i] for i in indices]
            
        log_debug(f"StateManager: Salvando {len(target_pages)} páginas em {path}")
        new_doc = fitz.open()
        
        for i, p in enumerate(target_pages):
            try:
                new_doc.insert_pdf(
                    p.source_doc, 
                    from_page=p.source_page_index, 
                    to_page=p.source_page_index, 
                    rotate=p.rotation_offset 
                )
            except Exception as e:
                log_error(f"StateManager: Erro ao inserir página {i}: {e}")
            
        new_doc.save(path)
        new_doc.close()
        log_debug("StateManager: Salvo com sucesso.")

    def get_page(self, index: int) -> Optional[VirtualPage]:
        if 0 <= index < len(self.pages):
            return self.pages[index]
        return None

    def close_all(self):
        self.pages = []
        for doc in self._docs_keep_alive:
            doc.close()
        self._docs_keep_alive = []
