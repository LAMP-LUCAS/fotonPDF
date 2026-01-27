from PyQt6.QtWidgets import QListWidget, QListWidgetItem, QAbstractItemView
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import QSize, pyqtSignal, Qt, QTimer
from src.interfaces.gui.utils.ui_error_boundary import ResilientWidget

class ThumbnailPanel(ResilientWidget):
    """Painel lateral resiliente com suporte a miniaturas."""
    pageSelected = pyqtSignal(int)
    orderChanged = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self._current_session = 0
        
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
        self._current_session += 1
        self.list.clear()
        if page_count == 0:
            self.show_placeholder(True, "O documento está vazio.")
            return
            
        self.show_placeholder(False)
        self.append_thumbnails(path, page_count, self._current_session)

    def append_thumbnails(self, path: str, page_count: int, session_id: int):
        """Adiciona miniaturas de forma progressiva em lotes para manter a GUI ativa."""
        batch_size = 20
        
        def process_batch(current_start):
            # Cancelamento por sessão: se o ID mudou, abortar este lote
            if session_id != self._current_session:
                return
                
            if current_start >= page_count:
                return
                
            self.list.setUpdatesEnabled(False)
            end_idx = min(current_start + batch_size, page_count)
            
            from src.interfaces.gui.state.render_engine import RenderEngine
            engine = RenderEngine.instance()
            
            for i in range(current_start, end_idx):
                item = QListWidgetItem(f"Página {i + 1}")
                item.setData(Qt.ItemDataRole.UserRole, i)
                self.list.addItem(item)
                
                # Solicitar render (O motor já é assíncrono)
                engine.request_render(
                    path, i, 0.2, 0, 
                    lambda p_idx, pix, z, r, m, it=item, sid=session_id: self._on_thumbnail_ready(it, pix, sid)
                )
            
            self.list.setUpdatesEnabled(True)
            
            # Agendar próximo lote
            if end_idx < page_count:
                QTimer.singleShot(50, lambda: process_batch(end_idx))

        process_batch(0)

    def _on_thumbnail_ready(self, item, pixmap, session_id):
        # Proteção final: só atualizar se ainda for a mesma sessão
        if session_id == self._current_session and item:
            item.setIcon(QIcon(pixmap))

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
