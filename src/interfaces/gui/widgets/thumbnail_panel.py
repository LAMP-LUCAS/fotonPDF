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
        self.setFlow(QListWidget.Flow.TopToBottom)
        self.setMovement(QAbstractItemView.Movement.Static)
        self.setStyleSheet("""
            QListWidget {
                background-color: #252525;
                border: none;
                color: white;
            }
            QListWidget::item:selected {
                background-color: #3d3d3d;
                border-left: 3px solid #4CAF50;
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

    def _on_item_clicked(self, item):
        page_num = item.data(Qt.ItemDataRole.UserRole)
        self.pageSelected.emit(page_num)
