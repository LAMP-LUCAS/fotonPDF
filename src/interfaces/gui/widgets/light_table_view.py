from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem, QGraphicsPixmapItem
from PyQt6.QtCore import Qt, QPointF, QRectF, pyqtSignal, QTimer
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QPixmap

class PageItem(QGraphicsPixmapItem):
    """Representa uma página PDF individual na Mesa de Luz."""
    moved = pyqtSignal(int, float, float) # page_idx, x, y

    def __init__(self, page_index, source_path):
        super().__init__()
        self.page_index = page_index
        self.source_path = source_path
        
        # Estilo base
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        
        # Render inicial placeholder
        from src.interfaces.gui.state.render_engine import RenderEngine
        RenderEngine.instance().request_render(
            source_path, page_index, 0.3, 0, 
            lambda idx, pix, z, r, m, c: self.setPixmap(pix)
        )

    def itemChange(self, change, value):
        if change == QGraphicsPixmapItem.GraphicsItemChange.ItemPositionHasChanged:
            # Check if scene is valid before emitting (item may be removed during transitions)
            scene = self.scene()
            if scene and hasattr(scene, 'pageMoved'):
                pos = self.pos()
                scene.pageMoved.emit(self.page_index, pos.x(), pos.y())
        return super().itemChange(change, value)

class LightTableView(QGraphicsView):
    """Mesa de Luz: visualização de páginas como objetos físicos arrastáveis."""
    pageMoved = pyqtSignal(int, float, float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("LightTableView")
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.scene.pageMoved = self.pageMoved # Pass-through manual
        self.scene.setBackgroundBrush(QColor("#0F172A"))
        
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        
        self.setStyleSheet("border: none; background-color: #0F172A;")

    def load_document(self, path, metadata):
        """Carrega os itens da cena de forma progressiva para evitar travamento da GUI."""
        self.scene.clear()
        page_count = metadata.get("page_count", 0)
        spacing = 350
        cols = 3
        batch_size = 10
        
        def process_batch(current_start):
            if current_start >= page_count:
                return
                
            self.viewport().setUpdatesEnabled(False)
            end_idx = min(current_start + batch_size, page_count)
            
            for i in range(current_start, end_idx):
                item = PageItem(i, str(path))
                row, col = i // cols, i % cols
                item.setPos(col * spacing, row * spacing)
                self.scene.addItem(item)
            
            self.viewport().setUpdatesEnabled(True)
            
            if end_idx < page_count:
                QTimer.singleShot(30, lambda: process_batch(end_idx))

        process_batch(0)
