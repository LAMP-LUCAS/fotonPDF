from PyQt6.QtWidgets import QListWidget, QListWidgetItem, QAbstractItemView
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import QSize, pyqtSignal, Qt
from src.interfaces.gui.utils.ui_error_boundary import ResilientWidget

class ThumbnailPanel(ResilientWidget):
    """Painel lateral resiliente com suporte a miniaturas."""
    pageSelected = pyqtSignal(int)
    orderChanged = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        
        # O widget base do ResilientWidget agora é um QListWidget
        self.list = QListWidget()
        self.list.setFixedWidth(220)
        self.list.setIconSize(QSize(120, 160))
        self.list.setGridSize(QSize(140, 180))
        self.list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.list.setFlow(QListWidget.Flow.LeftToRight)
        self.list.setWrapping(True)
        self.list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.list.setMovement(QListWidget.Movement.Free)
        self.list.setDragEnabled(True)
        self.list.setAcceptDrops(True)
        self.list.setDropIndicatorShown(True)
        self.list.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.list.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        
        self.list.setStyleSheet("background: transparent; border: none;")
        self.list.itemClicked.connect(self._on_item_clicked)
        
        self.set_content_widget(self.list)
        self.show_placeholder(True, "Nenhuma página carregada")

    def load_thumbnails(self, path: str, page_count: int):
        self.list.clear()
        if page_count == 0:
            self.show_placeholder(True, "O documento está vazio.")
            return
            
        self.show_placeholder(False)
        self.append_thumbnails(path, page_count)

    def append_thumbnails(self, path: str, page_count: int):
        start_idx = self.list.count()
        for i in range(page_count):
            absolute_idx = start_idx + i
            item = QListWidgetItem(f"Página {absolute_idx + 1}")
            item.setData(Qt.ItemDataRole.UserRole, absolute_idx)
            self.list.addItem(item)
            
            from src.interfaces.gui.state.render_engine import RenderEngine
            RenderEngine.instance().request_render(
                path, i, 0.2, 0, 
                lambda p_idx, pix, z, r, m, it=item: self._on_thumbnail_ready(it, pix)
            )

    def _on_thumbnail_ready(self, item, pixmap):
        if item: item.setIcon(QIcon(pixmap))

    def _on_item_clicked(self, item):
        self.pageSelected.emit(self.list.row(item))

    def get_selected_rows(self) -> list[int]:
        return sorted([self.list.row(item) for item in self.list.selectedItems()])

    def set_selected_page(self, index: int):
        if 0 <= index < self.list.count():
            item = self.list.item(index)
            self.list.setCurrentItem(item)
            item.setSelected(True)
            self.list.scrollToItem(item)
