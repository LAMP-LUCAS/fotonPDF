from PyQt6.QtWidgets import QListWidget, QListWidgetItem, QAbstractItemView
from PyQt6.QtGui import QIcon, QPixmap, QImage
from PyQt6.QtCore import QSize, pyqtSignal, Qt
import fitz

class ThumbnailPanel(QListWidget):
    """Painel lateral com suporte a adição incremental de miniaturas."""
    pageSelected = pyqtSignal(int)
    orderChanged = pyqtSignal(list)

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
        
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        
        self.setStyleSheet("""
            QListWidget { background-color: #1e1e1e; border-right: 1px solid #333; color: white; }
            QListWidget::item { border-radius: 5px; margin: 5px; padding: 10px; }
            QListWidget::item:selected { background-color: #2e2e2e; border: 2px solid #4CAF50; }
        """)
        self.itemClicked.connect(self._on_item_clicked)

    def dropEvent(self, event):
        super().dropEvent(event)
        new_order = []
        for i in range(self.count()):
            # O UserRole agora deve mapear para o índice VISUAL na lista de widgets do Viewer
            # Na verdade, o 'reorder' do MainWindow recebe índices visuais (0, 1, 2...)
            # Então apenas emitimos a lista de UserRoles que inserimos.
            new_order.append(self.item(i).data(Qt.ItemDataRole.UserRole))
        self.orderChanged.emit(new_order)

    def load_thumbnails(self, path: str):
        self.clear()
        self.append_thumbnails(path)

    def append_thumbnails(self, path: str):
        """Adiciona miniaturas de um documento ao final da lista."""
        doc = fitz.open(path)
        start_idx = self.count()
        
        for i in range(len(doc)):
            page = doc.load_page(i)
            pix = page.get_pixmap(matrix=fitz.Matrix(0.2, 0.2), alpha=False)
            
            img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888)
            
            # O UserRole armazena o índice ABSOLUTO na lista de páginas atual
            # (que corresponde à ordem em que foram adicionadas inicialmente)
            absolute_idx = start_idx + i
            item = QListWidgetItem(f"Página {absolute_idx + 1}")
            item.setIcon(QIcon(QPixmap.fromImage(img)))
            item.setData(Qt.ItemDataRole.UserRole, absolute_idx)
            self.addItem(item)
            
        doc.close()

    def _on_item_clicked(self, item):
        # Emite o índice visual atual para scroll
        self.pageSelected.emit(self.row(item))

    def get_selected_rows(self) -> list[int]:
        """IDs visuais (linhas) das páginas selecionadas."""
        return sorted([self.row(item) for item in self.selectedItems()])

    def get_selected_pages(self) -> list[int]:
        """IDs absolutos (UserRole) das páginas selecionadas (legado)."""
        return sorted([item.data(Qt.ItemDataRole.UserRole) for item in self.selectedItems()])
