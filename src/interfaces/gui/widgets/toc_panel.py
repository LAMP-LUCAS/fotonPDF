from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem, QLabel
from PyQt6.QtCore import pyqtSignal, Qt, QThread
from src.interfaces.gui.utils.ui_error_boundary import ResilientWidget
from src.infrastructure.services.logger import log_debug, log_exception

class AsyncTOCWorker(QThread):
    """Worker para extrair o sumário em background."""
    finished = pyqtSignal(list, int) # items, session_id
    error = pyqtSignal(str)

    def __init__(self, use_case, pdf_path, session_id):
        super().__init__()
        self.use_case = use_case
        self.pdf_path = pdf_path
        self.session_id = session_id

    def run(self):
        try:
            log_debug(f"TOCWorker [S{self.session_id}]: Extraindo de {self.pdf_path.name}")
            items = self.use_case.execute(self.pdf_path)
            self.finished.emit(items, self.session_id)
        except Exception as e:
            log_exception(f"TOCWorker Error: {e}")
            self.error.emit(str(e))

class TOCPanel(ResilientWidget):
    """Painel lateral resiliente para Sumário (Bookmarks)."""
    bookmark_clicked = pyqtSignal(int, str) # page_index, pdf_path

    def __init__(self, get_toc_use_case):
        super().__init__()
        self._get_toc_use_case = get_toc_use_case
        self._pdf_path = None
        self._worker = None
        self._current_session = 0
        
        # Widget interno da árvore
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.itemClicked.connect(self._on_item_clicked)
        self.tree.setStyleSheet("background: transparent; border: none;")
        
        self.set_content_widget(self.tree)
        self.show_placeholder(True, "Nenhum documento carregado")

    def set_pdf(self, path):
        # Evitar recarga se for o mesmo arquivo
        if self._pdf_path == path:
            return
            
        self._pdf_path = path
        self.load_toc()

    def load_toc(self):
        if not self._pdf_path:
            self.show_placeholder(True, "Nenhum documento carregado")
            return
            
        self._current_session += 1
        
        # REMOVIDO: worker.terminate() (Inscuro). Usamos verificação de ID na volta.
        # if self._worker and self._worker.isRunning(): ...

        self.tree.clear()
        self.show_placeholder(True, "Carregando Sumário...")
        
        self._worker = AsyncTOCWorker(self._get_toc_use_case, self._pdf_path, self._current_session)
        self._worker.finished.connect(self._on_toc_ready)
        self._worker.error.connect(lambda e: self.show_placeholder(True, f"Erro: {e}"))
        self._worker.start()

    def _on_toc_ready(self, items, session_id):
        # Validação de Sessão: Ignorar se um novo arquivo já foi carregado
        if session_id != self._current_session:
            log_debug(f"TOCPanel: Ignorando resultado de sessão antiga (R:{session_id} != C:{self._current_session})")
            return
            
        if not items:
            self.show_placeholder(True, "Este documento não possui Sumário técnico.")
            return
            
        try:
            self.show_placeholder(False)
            self.tree.setUpdatesEnabled(False) # Performance: evitar repaints durante construção
            
            stack = [(0, self.tree.invisibleRootItem())]
            for item in items:
                while stack and stack[-1][0] >= item.level:
                    stack.pop()
                
                if not stack:
                    # Fallback para evitar erro de stack vazia se level for estranho
                    parent_item = self.tree.invisibleRootItem()
                else:
                    parent_item = stack[-1][1]
                    
                tree_item = QTreeWidgetItem(parent_item)
                tree_item.setText(0, item.title)
                tree_item.setData(0, Qt.ItemDataRole.UserRole, item.page_index)
                stack.append((item.level, tree_item))
            
            self.tree.expandAll()
            self.tree.setUpdatesEnabled(True)
            
        except Exception as e:
            self.show_placeholder(True, f"Erro ao montar árvore: {str(e)}")

    def _on_item_clicked(self, item, column):
        page_index = item.data(0, Qt.ItemDataRole.UserRole)
        if page_index is not None:
            self.bookmark_clicked.emit(page_index, str(self._pdf_path))
