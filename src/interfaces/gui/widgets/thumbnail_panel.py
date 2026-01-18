from PyQt6.QtWidgets import QListWidget, QListWidgetItem, QAbstractItemView
from PyQt6.QtGui import QIcon, QPixmap, QImage
from PyQt6.QtCore import QSize, pyqtSignal, Qt
import fitz

class ThumbnailPanel(QListWidget):
    """Painel lateral com miniaturas para navegação rápida e reordenação."""
    pageSelected = pyqtSignal(int)
    orderChanged = pyqtSignal(list) # Lista de novos índices

    def __init__(self):
        super().__init__()
        self.setFixedWidth(220)
        self.setIconSize(QSize(120, 160))
        self.setGridSize(QSize(140, 180))
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setFlow(QListWidget.Flow.LeftToRight)
        self.setWrapping(True)
        self.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.setMovement(QListWidget.Movement.Free)
        
        # Drag & Drop Reordering
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
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

    def dropEvent(self, event):
        """Detecta o drop e emite sinal de mudança de ordem."""
        super().dropEvent(event)
        new_order = []
        for i in range(self.count()):
            item = self.item(i)
            new_order.append(item.data(Qt.ItemDataRole.UserRole))
        self.orderChanged.emit(new_order)

    def load_thumbnails(self, doc):
        self.clear()
        for i in range(len(doc)):
            page = doc.load_page(i)
            # Miniatura menor para performance e compatibilidade de cor
            # alpha=False garante fundo branco (padrão PDF) mas retorna RGB (3 bytes)
            pix = page.get_pixmap(matrix=fitz.Matrix(0.2, 0.2), alpha=False)
            
            fmt = QImage.Format.Format_RGB888
            img = QImage(pix.samples, pix.width, pix.height, pix.stride, fmt)
            
            item = QListWidgetItem(f"Página {i+1}")
            item.setIcon(QIcon(QPixmap.fromImage(img)))
            item.setData(Qt.ItemDataRole.UserRole, i)
            self.addItem(item)

    def _on_item_clicked(self, item):
        page_num = item.data(Qt.ItemDataRole.UserRole)
        self.pageSelected.emit(page_num)

    def get_selected_pages(self) -> list[int]:
        """Retorna os números das páginas selecionadas (1-based)."""
        selected_items = self.selectedItems()
        # UserRole armazena o 0-based index. Retornamos 1-based para o Caso de Uso.
        pages = [item.data(Qt.ItemDataRole.UserRole) + 1 for item in selected_items]
        return sorted(pages)
