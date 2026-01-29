from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPixmap, QPainter, QColor, QBrush
from PyQt6.QtCore import Qt, QRectF
from pathlib import Path
from src.infrastructure.services.logger import log_debug, log_error, log_exception
from src.interfaces.gui.state.render_engine import RenderEngine
from src.infrastructure.services.telemetry_service import TelemetryService

class PageWidget(QLabel):
    """Widget de página que conhece sua própria origem (Source Path/Index)."""

    def __init__(self, source_path: str, source_index: int, width_pt=0, height_pt=0, parent=None):
        super().__init__(parent)
        self.source_path = source_path
        self.source_index = source_index
        self.width_pt = width_pt
        self.height_pt = height_pt
        self.zoom = 1.0
        self.rotation = 0
        self.mode = "default"
        
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("background-color: white; border: 1px solid #111;")
        
        # Inicializar com tamanho fixo se dimensões conhecidas
        if width_pt > 0 and height_pt > 0:
            self.setFixedSize(int(width_pt * self.zoom), int(height_pt * self.zoom))
        else:
            self.setMinimumHeight(400) # Fallback
            
        self._rendered = False
        self._highlights = [] # list[QRectF] em pontos PDF
        self._base_pixmap = None

    def update_layout_size(self, zoom: float):
        """Define o tamanho físico do widget ANTES da renderização para estabilizar o scroll."""
        old_zoom = self.zoom
        self.zoom = zoom
        if self.width_pt > 0 and self.height_pt > 0:
            # Check rotation for dimension swappping
            is_rotated = (self.rotation % 180 != 0)
            
            w = self.height_pt if is_rotated else self.width_pt
            h = self.width_pt if is_rotated else self.height_pt
            
            new_w = int(w * zoom)
            new_h = int(h * zoom)
            
            if self.size() != (new_w, new_h):
                self.setFixedSize(new_w, new_h)
                # Se o zoom mudou, o cache antigo é inválido
                self._base_pixmap = None
                # CRÍTICO: Marcar como não renderizado para forçar nova requisição
                self._rendered = False


    def render_page(self, zoom=None, rotation=None, mode=None, force=False, clip=None, priority=0):
        """Solicita renderização. Suporta 'clip' para Tiling em arquivos pesados."""
        try:
            should_render = force
            
            if zoom is not None and abs(self.zoom - zoom) > 0.001:
                should_render = True
                self.update_layout_size(zoom)
            
            if rotation is not None and self.rotation != rotation:
                should_render = True
                self.rotation = rotation
                self.update_layout_size(self.zoom)

            if mode is not None and self.mode != mode:
                should_render = True
                self.mode = mode
            
            if not should_render and self._rendered and clip is None:
                return
            
            # Feedback visual de carregamento
            if not self._rendered and self._base_pixmap is None:
                self.setStyleSheet("background-color: #2D2D2D; border: 1px solid #444;")

            # O RenderEngine gerencia a fila
            RenderEngine.instance().request_render(
                self.source_path, 
                self.source_index, 
                self.zoom, 
                self.rotation, 
                self.on_render_finished,
                mode=self.mode,
                clip=clip,
                priority=priority
            )
        except Exception as e:
            log_exception(f"PageWidget: Erro ao solicitar render: {e}")

    def on_render_finished(self, page_num, pixmap, zoom, rotation, mode, clip):
        """Callback do motor central. Gerencia se é um frame completo ou um tile."""
        if page_num != self.source_index: return
        if abs(zoom - self.zoom) > 0.001 or rotation != self.rotation or mode != self.mode: return

        try:
            if pixmap.isNull(): return
                
            if clip is None:
                # Renderização Completa
                self._base_pixmap = pixmap
                self.setPixmap(self._base_pixmap)
            else:
                # Renderização de Tile (Bloco)
                # Se ainda não temos um pixmap base do tamanho certo, criamos um vazio
                if self._base_pixmap is None or self._base_pixmap.size() != self.size():
                    self._base_pixmap = QPixmap(self.size())
                    bg = QColor(255, 255, 255) if mode == "default" else QColor(30, 30, 30)
                    self._base_pixmap.fill(bg)
                
                # Compor o tile no pixmap base na posição correta
                painter = QPainter(self._base_pixmap)
                tx = int(clip[0] * zoom)
                ty = int(clip[1] * zoom)
                painter.drawPixmap(tx, ty, pixmap)
                painter.end()
                
                self.setPixmap(self._base_pixmap)
            
            # Se for a primeira página, registrar o TTU (Time to Usability)
            if self.source_index == 0:
                TelemetryService.log_operation("TTU", Path(self.source_path))

            self._rendered = True
            self.setStyleSheet("background-color: white; border: 1px solid #111;")
            self.setMinimumHeight(0)
        except Exception as e:
            log_exception(f"PageWidget: Erro ao atualizar UI: {e}")

            self.setMinimumHeight(0)
        except Exception as e:
            log_exception(f"PageWidget: Erro ao atualizar UI: {e}")
