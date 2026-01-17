from PyQt6.QtWidgets import QListWidget, QListWidgetItem, QAbstractItemView
from PyQt6.QtGui import QIcon, QPixmap, QImage
from PyQt6.QtCore import QSize, pyqtSignal
import fitz

class ThumbnailPanel(QListWidget):
    """Painel lateral com miniaturas para navegação rápida."""
    pageSelected = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setFixedWidth(200)
        self.setIconSize(QSize(150, 200))
        self.setGridSize(QSize(180, 220))
        self.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.setFlow(QListWidget.Flow.TopToBottom)
        self.setMovement(QAbstractItemView.Movement.Static)
        self.setStyleSheet("""
            QListWidget {
                background-color: #1e1e1e;
                border-right: 1px solid #333;
                color: white;
            }
            QListWidget::item {
                border-radius: 5px;
                margin: 5px;
                padding: 10px;
            }
            QListWidget::item:selected {
                background-color: #2e2e2e;
                border: 2px solid #4CAF50;
            }
            QListWidget::item:hover {
                background-color: #252525;
            }
        """)
        self.itemClicked.connect(self._on_item_clicked)

    def load_thumbnails(self, doc):
        self.clear()
        for i in range(len(doc)):
            page = doc.load_page(i)
            # Miniatura menor para performance
            pix = page.get_pixmap(matrix=fitz.Matrix(0.2, 0.2))
            
            fmt = QImage.Format.Format_RGBA8888
            img = QImage(pix.samples, pix.width, pix.height, pix.stride, fmt)
            
            item = QListWidgetItem(f"Página {i+1}")
            item.setIcon(QIcon(QPixmap.fromImage(img)))
            item.setData(Qt.ItemDataRole.UserRole, i)
            self.addItem(item)

    def get_selected_pages(self) -> list[int]:
        """Retorna os números das páginas selecionadas (1-based)."""
        selected_items = self.selectedItems()
        # UserRole armazena o 0-based index. Retornamos 1-based para o Caso de Uso.
        pages = [item.data(Qt.ItemDataRole.UserRole) + 1 for item in selected_items]
        return sorted(pages)
