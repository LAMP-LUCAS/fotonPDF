from pathlib import Path
import fitz
from PyQt6.QtWidgets import QScrollArea, QVBoxLayout, QWidget, QFrame
from PyQt6.QtCore import Qt, QTimer
from src.interfaces.gui.widgets.page_widget import PageWidget
from src.infrastructure.services.logger import log_debug, log_warning
from src.interfaces.gui.state.render_engine import RenderEngine

class PDFViewerWidget(QScrollArea):
    """Widget de visualização estável com suporte a Fila de Renderização Centralizada."""

    def __init__(self):
        super().__init__()
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setStyleSheet("background-color: #1e1e1e;") 
        
        self.container = QWidget()
        self.layout = QVBoxLayout(self.container)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.setSpacing(30)
        self.layout.setContentsMargins(40, 40, 40, 40)
        
        self.setWidget(self.container)
        self._doc = None
        self._doc_path = None
        self._placeholder = None
        self._pages = []
        self._zoom = 1.0
        self._panning = False
        self._last_mouse_pos = None

        # Conectar scroll para renderização preguiçosa
        self.verticalScrollBar().valueChanged.connect(self.check_visibility)

    def has_document(self) -> bool:
        return self._doc is not None

    def setPlaceholder(self, widget: QWidget):
        if self._placeholder:
            self._placeholder.deleteLater()
        self._placeholder = widget
        self.layout.addWidget(widget)

    def set_zoom(self, zoom: float):
        if not self._doc:
            return
        self._zoom = max(0.2, min(zoom, 5.0))
        # Ao mudar zoom, opcionalmente limpar fila pendente
        # RenderEngine.instance().cancel_all()
        self.check_visibility()

    def zoom_in(self):
        self.set_zoom(self._zoom * 1.2)

    def zoom_out(self):
        self.set_zoom(self._zoom / 1.2)

    def fit_width(self):
        if not self._pages or not self._doc:
            return
        page_width = self._doc[0].rect.width
        available_width = self.viewport().width() - 100
        self.set_zoom(available_width / page_width)

    def fit_height(self):
        if not self._pages or not self._doc:
            return
        page_height = self._doc[0].rect.height
        available_height = self.viewport().height() - 100
        self.set_zoom(available_height / page_height)

    def real_size(self):
        self.set_zoom(1.0)

    def load_document(self, path: Path):
        """Carrega novo documento com limpeza rigorosa de recursos."""
        # 1. Cancelar renderizações pendentes do arquivo anterior
        RenderEngine.instance().cancel_all()
        
        # 2. Fechar handle do documento atual
        if self._doc:
            self._doc.close()
            self._doc = None
            
        if self._placeholder:
            self._placeholder.hide()
            
        # 3. Limpar widgets de página
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        self._pages = []
        self._doc_path = str(path)
        self._doc = fitz.open(self._doc_path)
        
        log_debug(f"Viewer: Carregando {path.name} ({len(self._doc)} páginas)")
        
        for i in range(len(self._doc)):
            page_widget = PageWidget(i)
            self.layout.addWidget(page_widget)
            self._pages.append(page_widget)
        
        self.verticalScrollBar().setValue(0)
        # Timer para garantir estabilização do layout antes da primeira renderização
        QTimer.singleShot(200, self._initial_render)
        
        return self._doc

    def _initial_render(self):
        if not self._doc: return
        self.fit_width()
        self.check_visibility()

    def refresh_page(self, index: int, rotation: int = None):
        if 0 <= index < len(self._pages):
            page_widget = self._pages[index]
            if rotation is not None:
                page_widget.rotation = rotation
            page_widget._rendered = False
            self.check_visibility()

    def check_visibility(self):
        """Identifica páginas visíveis e solicita renderização centralizada."""
        if not self._doc:
            return
            
        viewport_top = self.verticalScrollBar().value()
        viewport_bottom = viewport_top + self.height()
        buffer = 1200 # Margem de renderização antecipada
        
        for page in self._pages:
            pos = page.pos().y()
            if pos < viewport_bottom + buffer and pos + page.height() > viewport_top - buffer:
                # Solicita via caminho para garantir isolamento de handle se necessário,
                # embora o RenderEngine já trate do isolamento.
                page.render_page(self._doc_path, zoom=self._zoom)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._panning = True
            self._last_mouse_pos = event.position().toPoint()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self._panning = False
        self.setCursor(Qt.CursorShape.ArrowCursor)
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if self._panning:
            delta = event.position().toPoint() - self._last_mouse_pos
            self._last_mouse_pos = event.position().toPoint()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
        super().mouseMoveEvent(event)

    def wheelEvent(self, event):
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if event.angleDelta().y() > 0: self.zoom_in()
            else: self.zoom_out()
            event.accept()
        else:
            super().wheelEvent(event)

    def reorder_pages(self, new_order: list[int]):
        if not self._pages: return
        widgets_map = {p.page_num: p for p in self._pages}
        for i in reversed(range(self.layout.count())):
            item = self.layout.takeAt(i)
            if item.widget(): item.widget().setParent(None)
        
        new_pages_list = []
        for orig_idx in new_order:
            widget = widgets_map[orig_idx]
            self.layout.addWidget(widget)
            new_pages_list.append(widget)
        
        self._pages = new_pages_list
        self.check_visibility()

    def closeEvent(self, event):
        RenderEngine.instance().cancel_all()
        if self._doc:
            self._doc.close()
        super().closeEvent(event)
