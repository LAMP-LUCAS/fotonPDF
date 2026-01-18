from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
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
        
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("background-color: white; border: 1px solid #111;")
        self.setMinimumHeight(400) # Placeholder
        self._rendered = False

    def render_page(self, zoom=None, rotation=None):
        """Solicita renderização usando sua própria origem."""
        try:
            should_render = False
            
            if zoom is not None and abs(self.zoom - zoom) > 0.001:
                should_render = True
                self.zoom = zoom
            
            if rotation is not None and self.rotation != rotation:
                should_render = True
                self.rotation = rotation
            
            if not should_render and self._rendered:
                return
            
            self._rendered = False
            # O RenderEngine gerencia a fila e as threads
            RenderEngine.instance().request_render(
                self.source_path, 
                self.source_index, 
                self.zoom, 
                self.rotation, 
                self.on_render_finished
            )
        except Exception as e:
            log_exception(f"PageWidget: Erro ao solicitar render: {e}")

    def on_render_finished(self, page_num, pixmap, zoom, rotation):
        """Callback do motor central."""
        # Verificar se ainda é a mesma origem e o mesmo zoom solicitado
        if page_num != self.source_index:
            return
            
        if abs(zoom - self.zoom) > 0.001 or rotation != self.rotation:
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
