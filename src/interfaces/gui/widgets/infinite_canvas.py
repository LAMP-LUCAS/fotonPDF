from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QFrame
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QWheelEvent

class InfiniteCanvasView(QGraphicsView):
    """Visualizador de alta performance (Infinite Canvas) para plantas complexas."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("InfiniteCanvas")
        
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.scene.setBackgroundBrush(QColor("#1a1a1a"))
        
        # Otimizações de Renderização
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.SmartViewportUpdate)
        
        # Remover barras de rolagem para feeling de canvas
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.setStyleSheet("border: none; background-color: #1a1a1a;")
        
        self._draw_mock_grid()

    def _draw_mock_grid(self):
        """Desenha um grid de engenharia e uma folha A0 mockada."""
        # Grid suave
        grid_pen = QPen(QColor("#2a2a2a"), 0.5)
        major_grid_pen = QPen(QColor("#333333"), 1)
        
        for x in range(-2000, 4000, 50):
            pen = major_grid_pen if x % 200 == 0 else grid_pen
            self.scene.addLine(x, -2000, x, 4000, pen)
        for y in range(-2000, 4000, 50):
            pen = major_grid_pen if y % 200 == 0 else grid_pen
            self.scene.addLine(-2000, y, 4000, y, pen)
            
        # Folha A0 (841 x 1189 mm -> pixels aprox)
        paper_shadow = self.scene.addRect(5, 5, 1189, 841, QPen(Qt.PenStyle.NoPen), QBrush(QColor("#0a0a0a")))
        paper = self.scene.addRect(0, 0, 1189, 841, QPen(QColor("#3a3a3a")), QBrush(QColor("#fafafa")))
        
        # Mock de planta baixa
        blueprint_pen = QPen(QColor("#3498db"), 2)
        self.scene.addRect(100, 100, 400, 300, blueprint_pen) # Sala
        self.scene.addRect(500, 100, 300, 300, blueprint_pen) # Cozinha
        self.scene.addText("PLANTA BAIXA - RESIDÊNCIA MODELO", self.scene.font()).setPos(100, 50)
        
        # Centralizar na folha
        self.centerOn(594, 420)

    def wheelEvent(self, event: QWheelEvent):
        """Zoom suave estilo CAD."""
        zoom_in_factor = 1.15
        zoom_out_factor = 1 / zoom_in_factor

        if event.angleDelta().y() > 0:
            self.scale(zoom_in_factor, zoom_in_factor)
        else:
            self.scale(zoom_out_factor, zoom_out_factor)
