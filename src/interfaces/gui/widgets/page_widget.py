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
        self.zoom = zoom
        if self.width_pt > 0 and self.height_pt > 0:
            new_w = int(self.width_pt * zoom)
            new_h = int(self.height_pt * zoom)
            if self.size() != (new_w, new_h):
                self.setFixedSize(new_w, new_h)
                # Se o zoom mudou, o cache antigo é inválido
                self._base_pixmap = None

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
