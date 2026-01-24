from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem, QGraphicsPixmapItem
from PyQt6.QtCore import Qt, QPointF, QRectF, pyqtSignal
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
            lambda idx, pix, z, r, m: self.setPixmap(pix)
        )

    def itemChange(self, change, value):
        if change == QGraphicsPixmapItem.GraphicsItemChange.ItemPositionHasChanged:
            pos = self.pos()
            self.scene().pageMoved.emit(self.page_index, pos.x(), pos.y())
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
        self.scene.clear()
        page_count = metadata.get("page_count", 0)
        spacing = 350
        cols = 3
        
        for i in range(page_count):
            item = PageItem(i, str(path))
            row, col = i // cols, i % cols
            item.setPos(col * spacing, row * spacing)
            self.scene.addItem(item)
