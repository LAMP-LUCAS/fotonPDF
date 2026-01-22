from PyQt6.QtWidgets import QListWidget, QListWidgetItem, QAbstractItemView
from PyQt6.QtGui import QIcon, QPixmap, QImage
from PyQt6.QtCore import QSize, pyqtSignal, Qt

class ThumbnailPanel(QListWidget):
    """Painel lateral com suporte a exibição de miniaturas via sinal externo."""
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
            new_order.append(self.item(i).data(Qt.ItemDataRole.UserRole))
        self.orderChanged.emit(new_order)

    def load_thumbnails(self, path: str, page_count: int):
        """Limpa e inicia o carregamento de novas miniaturas."""
        self.clear()
        self.append_thumbnails(path, page_count)

    def append_thumbnails(self, path: str, page_count: int):
        """Adiciona placeholders de miniaturas. O carregamento real deve ser assíncrono via MainWindow/RenderEngine."""
        start_idx = self.count()
        
        for i in range(page_count):
            absolute_idx = start_idx + i
            item = QListWidgetItem(f"Página {absolute_idx + 1}")
            # Placeholder inicial
            item.setData(Qt.ItemDataRole.UserRole, absolute_idx)
            self.addItem(item)
            
            # Solicitar renderização da miniatura via RenderEngine (Zoom baixo)
            from src.interfaces.gui.state.render_engine import RenderEngine
            RenderEngine.instance().request_render(
                path, 
                i, 
                0.2, 
                0, 
                lambda p_idx, pix, z, r, m, it=item: self._on_thumbnail_ready(it, pix)
            )

    def _on_thumbnail_ready(self, item, pixmap):
        """Callback para atualizar o ícone do item quando a renderização termina."""
        if item:
            item.setIcon(QIcon(pixmap))

    def _on_item_clicked(self, item):
        # Emite o índice visual atual para scroll
        self.pageSelected.emit(self.row(item))

    def get_selected_rows(self) -> list[int]:
        """IDs visuais (linhas) das páginas selecionadas."""
        return sorted([self.row(item) for item in self.selectedItems()])

    def get_selected_pages(self) -> list[int]:
        """IDs absolutos (UserRole) das páginas selecionadas (legado)."""
        return sorted([item.data(Qt.ItemDataRole.UserRole) for item in self.selectedItems()])

    def set_selected_page(self, index: int):
        """Marca visualmente a página atual como selecionada."""
        if 0 <= index < self.count():
            item = self.item(index)
            self.setCurrentItem(item)
            # Garantir que o item visível seja selecionado e não apenas 'focado'
            item.setSelected(True)
            self.scrollToItem(item)
