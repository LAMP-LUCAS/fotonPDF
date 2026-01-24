from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem, QLabel
from PyQt6.QtCore import pyqtSignal, Qt
from src.interfaces.gui.utils.ui_error_boundary import ResilientWidget

class TOCPanel(ResilientWidget):
    """Painel lateral resiliente para Sumário (Bookmarks)."""
    bookmark_clicked = pyqtSignal(int)

    def __init__(self, get_toc_use_case):
        super().__init__()
        self._get_toc_use_case = get_toc_use_case
        self._pdf_path = None
        
        # Widget interno da árvore
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.itemClicked.connect(self._on_item_clicked)
        self.tree.setStyleSheet("background: transparent; border: none;")
        
        self.set_content_widget(self.tree)
        self.show_placeholder(True, "Nenhum documento carregado")

    def set_pdf(self, path):
        self._pdf_path = path
        self.load_toc()

    def load_toc(self):
        if not self._pdf_path:
            self.show_placeholder(True, "Nenhum documento carregado")
            return
            
        self.tree.clear()
        
        try:
            items = self._get_toc_use_case.execute(self._pdf_path)
            
            if not items:
                self.show_placeholder(True, "Este documento não possui Sumário técnico.")
                return
                
            self.show_placeholder(False)
            stack = [(0, self.tree.invisibleRootItem())]
            for item in items:
                while stack and stack[-1][0] >= item.level:
                    stack.pop()
                parent_item = stack[-1][1]
                tree_item = QTreeWidgetItem(parent_item)
                tree_item.setText(0, item.title)
                tree_item.setData(0, Qt.ItemDataRole.UserRole, item.page_index)
                stack.append((item.level, tree_item))
            self.tree.expandAll()
            
        except Exception as e:
            self.show_placeholder(True, f"Erro ao extrair sumário: {str(e)}")

    def _on_item_clicked(self, item, column):
        page_index = item.data(0, Qt.ItemDataRole.UserRole)
        if page_index is not None:
            self.bookmark_clicked.emit(page_index)
