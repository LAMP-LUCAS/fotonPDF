from PyQt6.QtWidgets import QScrollBar, QStyleOptionSlider, QStyle
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtCore import Qt, QRect

class MarkerScrollBar(QScrollBar):
    """Barra de rolagem com marcadores visuais (estilo VS Code)."""
    def __init__(self, orientation=Qt.Orientation.Vertical, parent=None):
        super().__init__(orientation, parent)
        self._markers = [] # Lista de floats (0.0 a 1.0) representando a posição proporcional

    def set_markers(self, positions: list[float]):
        self._markers = positions
        self.update()

    def paintEvent(self, event):
        # Primeiro, desenha a barra normal
        super().paintEvent(event)
        
        if not self._markers:
            return

        painter = QPainter(self)
        # Marcador estilo VS Code: Amarelo para busca, Azul para modificações, etc.
        # Usaremos Amarelo (#FFB100) para busca.
        color = QColor("#FFB100")
        painter.setPen(QPen(color, 2))
        
        # Área útil do track (descontando os botões de seta se existirem)
        # No estilo clean, geralmente não há botões, mas vamos calcular a geometria.
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        track_rect = self.style().subControlRect(QStyle.ComplexControl.CC_ScrollBar, opt, QStyle.SubControl.SC_ScrollBarSlider, self)
        
        # Na verdade, os marcadores ficam no track, não no slider.
        # Vamos usar a altura total do widget para simplificar, já que as setas estão ocultas no CSS.
        total_height = self.height()
        
        for pos in self._markers:
            y = int(pos * total_height)
            painter.drawLine(0, y, self.width(), y)
        
        painter.end()
