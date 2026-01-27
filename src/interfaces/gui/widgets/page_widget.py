from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPixmap, QPainter, QColor, QBrush
from PyQt6.QtCore import Qt, QRectF
from pathlib import Path
from src.infrastructure.services.logger import log_debug, log_error, log_exception
from src.interfaces.gui.state.render_engine import RenderEngine
from src.infrastructure.services.telemetry_service import TelemetryService

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

    def render_page(self, zoom=None, rotation=None, mode=None, force=False, clip=None, priority=0):
        """Solicita renderização. Suporta 'clip' para Tiling em arquivos pesados."""
        try:
            should_render = force
            
            if zoom is not None and abs(self.zoom - zoom) > 0.001:
                should_render = True
                self.zoom = zoom
            
            if rotation is not None and self.rotation != rotation:
                should_render = True
                self.rotation = rotation

            if mode is not None and self.mode != mode:
                should_render = True
                self.mode = mode
            
            if not should_render and self._rendered and clip is None:
                return
            
            # Se for um clip novo, marcamos como carregando (visual feedback)
            if not self._rendered:
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
                self.setPixmap(pixmap)
                self.setFixedSize(pixmap.size())
            else:
                # Renderização de Tile (Bloco)
                # Se ainda não temos um pixmap base, criamos um vazio
                if self.pixmap() is None or self.pixmap().size() != self.size():
                    # Estimar tamanho total se necessário ou usar o atual
                    pass 
                
                # Para simplificar na Sprint atual e garantir 0 travamento:
                # Se for um clip, nós apenas atualizamos a imagem.
                self.setPixmap(pixmap)
                # Em versões futuras: usar QPainter para compor tiles no pixmap base
            
            # Se for a primeira página, registrar o TTU (Time to Usability)
            if self.source_index == 0:
                TelemetryService.log_operation("TTU", Path(self.source_path))

            self._rendered = True
            self.setStyleSheet("background-color: white; border: 1px solid #111;")
            self.setMinimumHeight(0)
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
