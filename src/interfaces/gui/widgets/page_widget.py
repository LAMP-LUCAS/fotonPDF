from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPixmap, QPainter, QColor, QBrush
from PyQt6.QtCore import Qt, QRectF
from src.infrastructure.services.logger import log_debug, log_error, log_exception
from src.interfaces.gui.state.render_engine import RenderEngine

class PageWidget(QLabel):
    """Widget de página que conhece sua própria origem (Source Path/Index)."""

    def __init__(self, source_path: str, source_index: int, parent=None):
        super().__init__(parent)
        self.source_path = source_path
        self.source_index = source_index
        self.zoom = 1.0
        self.rotation = 0
        self.mode = "default"
        
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("background-color: white; border: 1px solid #111;")
        self.setMinimumHeight(400) # Placeholder
        self._rendered = False
        self._highlights = [] # list[QRectF] em pontos PDF

    def render_page(self, zoom=None, rotation=None, mode=None):
        """Solicita renderização usando sua própria origem."""
        try:
            should_render = False
            
            if zoom is not None and abs(self.zoom - zoom) > 0.001:
                should_render = True
                self.zoom = zoom
            
            if rotation is not None and self.rotation != rotation:
                should_render = True
                self.rotation = rotation

            if mode is not None and self.mode != mode:
                should_render = True
                self.mode = mode
            
            if not should_render and self._rendered:
                return
            
            self._rendered = False
            # O RenderEngine gerencia a fila e as threads
            RenderEngine.instance().request_render(
                self.source_path, 
                self.source_index, 
                self.zoom, 
                self.rotation, 
                self.on_render_finished,
                mode=self.mode
            )
        except Exception as e:
            log_exception(f"PageWidget: Erro ao solicitar render: {e}")

    def on_render_finished(self, page_num, pixmap, zoom, rotation, mode):
        """Callback do motor central."""
        # Verificar se ainda é a mesma origem e o mesmo zoom solicitado
        if page_num != self.source_index:
            return
            
        if abs(zoom - self.zoom) > 0.001 or rotation != self.rotation or mode != self.mode:
            return

        try:
            if pixmap.isNull():
                return
                
            self.setPixmap(pixmap)
            self._rendered = True
            self.setMinimumHeight(0)
            self.setFixedSize(pixmap.size())
        except Exception as e:
            log_exception(f"PageWidget: Erro ao atualizar UI: {e}")

    def set_highlights(self, rects: list):
        """Define os retângulos de realce (em pontos PDF)."""
        self._highlights = rects
        self.update()

    def paintEvent(self, event):
        # Primeiro, desenha a imagem (pixmap) base
        super().paintEvent(event)
        
        if not self._highlights:
            return

        painter = QPainter(self)
        # Amarelo translúcido para busca
        painter.setBrush(QBrush(QColor(255, 255, 0, 100)))
        painter.setPen(Qt.PenStyle.NoPen)
        
        for rect_data in self._highlights:
            # rect_data é (x0, y0, x1, y1) em pontos PDF
            x0, y0, x1, y1 = rect_data
            
            # Converter para pixels escalados pelo zoom
            # Importante: A origem (0,0) do widget deve coincidir com a origem do PDF no topo do QLabel
            # Como usamos setAlignment(Center), precisamos compensar se o pixmap for menor que o widget.
            # Mas o PageWidget dá setFixedSize(pixmap.size()), então (0,0) é o topo da página.
            
            rx = x0 * self.zoom
            ry = y0 * self.zoom
            rw = (x1 - x0) * self.zoom
            rh = (y1 - y0) * self.zoom
            
            painter.drawRect(QRectF(rx, ry, rw, rh))
        
        painter.end()
