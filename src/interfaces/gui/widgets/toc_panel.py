from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QLabel
from PyQt6.QtCore import pyqtSignal, Qt

class TOCPanel(QWidget):
    """Painel lateral para exibição do Sumário (Bookmarks)."""
    bookmark_clicked = pyqtSignal(int) # page_index

    def __init__(self, get_toc_use_case):
        super().__init__()
        self._get_toc_use_case = get_toc_use_case
        self._pdf_path = None
        
        self.layout = QVBoxLayout(self)
        
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.itemClicked.connect(self._on_item_clicked)
        
        self.layout.addWidget(self.tree)
        
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #7f8c8d; font-size: 10px;")
        self.layout.addWidget(self.status_label)

    def set_pdf(self, path):
        self._pdf_path = path
        self.load_toc()

    def load_toc(self):
        if not self._pdf_path:
            return
            
        self.tree.clear()
        
        try:
            items = self._get_toc_use_case.execute(self._pdf_path)
            
            if not items:
                self.status_label.setText("Documento sem sumário.")
                return
                
            # Pilha para gerenciar a hierarquia (níveis)
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
            self.status_label.setText(f"{len(items)} tópicos encontrados.")
            
        except Exception as e:
            self.status_label.setText("Não foi possível carregar o sumário.")

    def _on_item_clicked(self, item, column):
        page_index = item.data(0, Qt.ItemDataRole.UserRole)
        if page_index is not None:
            self.bookmark_clicked.emit(page_index)
