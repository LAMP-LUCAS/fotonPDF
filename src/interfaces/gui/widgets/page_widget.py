from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from src.infrastructure.services.logger import log_debug, log_error, log_exception
from src.interfaces.gui.state.render_engine import RenderEngine

class PageWidget(QLabel):
    """Widget de página que renderiza sob demanda via RenderEngine centralizado."""

    def __init__(self, page_num, parent=None):
        super().__init__(parent)
        self.page_num = page_num
        self.zoom = 1.0
        self.rotation = 0
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("background-color: white; border: 1px solid #111;")
        self.setMinimumHeight(400) # Placeholder height
        self._current_render_id = 0 # Para evitar atualizações de zoom obsoletas
        self._rendered = False

    def render_page(self, doc_path, zoom=None, rotation=None):
        try:
            should_render = False
            
            if zoom is not None and self.zoom != zoom:
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
                doc_path, 
                self.page_num, 
                self.zoom, 
                self.rotation, 
                self.on_render_finished
            )
        except Exception as e:
            log_exception(f"PageWidget: Erro ao solicitar render: {e}")

    def on_render_finished(self, page_num, pixmap, zoom, rotation):
        """Callback quando o RenderEngine termina uma tarefa."""
        # Verificar se ainda é a mesma página e o mesmo zoom/rotação solicitado
        if page_num != self.page_num:
            return
            
        if abs(zoom - self.zoom) > 0.001 or rotation != self.rotation:
            # log_debug(f"PageWidget: Descartando render obsoleto da página {page_num}")
            return

        try:
            if pixmap.isNull():
                return
                
            self.setPixmap(pixmap)
            self._rendered = True
            self.setMinimumHeight(0)
            self.setFixedSize(pixmap.size())
            # log_debug(f"PageWidget: Atualizada página {self.page_num}")
        except Exception as e:
            log_exception(f"PageWidget: Erro ao atualizar UI: {e}")
