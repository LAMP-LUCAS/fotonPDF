from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QFrame
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QWheelEvent

class InfiniteCanvasView(QGraphicsView):
    """
    Visualizador de alta performance (Infinite Canvas) para plantas complexas.
    Style: AEC-Dark Dot Grid.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("InfiniteCanvas")
        
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        # Background: Preto Absoluto (Definido no QSS, mas forçamos aqui para o canvas)
        self.setBackgroundBrush(QBrush(QColor("#0F0F11")))
        
        # Otimizações de Renderização
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.SmartViewportUpdate)
        
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setStyleSheet("border: none; background-color: #0F0F11;")
        
        # Mock de conteúdo (Folha A0)
        self._draw_mock_content()
        
    def _draw_mock_content(self):
        """Desenha apenas o conteúdo (folha), o grid é desenhado no background."""
        # Folha A0 (841 x 1189 mm)
        # Sombra da folha
        self.scene.addRect(5, 5, 1189, 841, QPen(Qt.PenStyle.NoPen), QBrush(QColor("#000000")))
        # Folha (Papel)
        paper_brush = QBrush(QColor("#1E1E1E")) # Papel Escuro para Dark Mode
        paper_pen = QPen(QColor("#3F3F46"))
        self.scene.addRect(0, 0, 1189, 841, paper_pen, paper_brush)
        
        # Mock de planta baixa (Blueprint Style)
        blueprint_pen = QPen(QColor("#3498db"), 2)
        blueprint_text = QColor("#FAFAFA")
        
        self.scene.addRect(100, 100, 400, 300, blueprint_pen) # Sala
        self.scene.addRect(500, 100, 300, 300, blueprint_pen) # Cozinha
        
        text = self.scene.addText("PLANTA BAIXA - AEC DARK MODE", self.scene.font())
        text.setDefaultTextColor(blueprint_text)
        text.setPos(100, 50)
        
        self.centerOn(594, 420)

    def drawBackground(self, painter, rect):
        """
        Desenha o Dot Grid (Grade de Pontos) de alta performance.
        Estilo: Pontos #3F3F46 a cada 40px.
        """
        # Preenche fundo
        painter.fillRect(rect, QColor("#0F0F11"))
        
        # Configura Pen para os pontos
        pen = QPen(QColor("#3F3F46"))
        pen.setWidth(2)
        painter.setPen(pen)
        
        # Grid Spacing
        grid_step = 40
        
        # Calcula limites visíveis
        l = int(rect.left())
        t = int(rect.top())
        r = int(rect.right())
        b = int(rect.bottom())
        
        # Ajusta para o grid
        first_left = l - (l % grid_step)
        first_top = t - (t % grid_step)
        
        # Desenha pontos
        points = []
        for x in range(first_left, r, grid_step):
            for y in range(first_top, b, grid_step):
                points.append(QPointF(x, y))
        
        if points:
            painter.drawPoints(points)

    def wheelEvent(self, event: QWheelEvent):
        """Zoom suave estilo CAD."""
        zoom_in_factor = 1.15
        zoom_out_factor = 1 / zoom_in_factor

        if event.angleDelta().y() > 0:
            self.scale(zoom_in_factor, zoom_in_factor)
        else:
            self.scale(zoom_out_factor, zoom_out_factor)
