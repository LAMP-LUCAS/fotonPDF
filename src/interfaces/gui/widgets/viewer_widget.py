from pathlib import Path
import fitz
from PyQt6.QtWidgets import QScrollArea, QVBoxLayout, QWidget, QFrame
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from src.interfaces.gui.widgets.page_widget import PageWidget
from src.infrastructure.services.logger import log_debug, log_warning
from src.interfaces.gui.state.render_engine import RenderEngine

class PDFViewerWidget(QScrollArea):
    """Visualizador que suporta documentos virtuais (múltiplas fontes)."""
    pageChanged = pyqtSignal(int)

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
        self._doc = None # Usado apenas para metadados/layout da 1ª página
        self._pages = []
        self._zoom = 1.0
        self._panning = False
        self._last_mouse_pos = None
        self._placeholder = None
        self._last_emitted_page = -1

        self.verticalScrollBar().valueChanged.connect(self.check_visibility)

    def clear(self):
        """Limpa o visualizador e encerra processos pendentes."""
        RenderEngine.instance().cancel_all()
        if self._doc:
            self._doc.close()
            self._doc = None
            
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self._pages = []

    def setPlaceholder(self, widget: QWidget):
        if self._placeholder: self._placeholder.deleteLater()
        self._placeholder = widget
        self.layout.addWidget(widget)

    def load_document(self, path: Path):
        """Inicializa o visualizador com um arquivo."""
        self.clear()
        if self._placeholder: self._placeholder.hide()
        
        self.add_pages(path)
        self.verticalScrollBar().setValue(0)
        QTimer.singleShot(200, self._initial_render)
        
        # Manter doc principal para cálculos de "fit"
        self._doc = fitz.open(str(path))
        return self._doc

    def add_pages(self, path: Path):
        """Adiciona páginas de um novo documento sem resetar."""
        path_str = str(path)
        temp_doc = fitz.open(path_str)
        num_pages = len(temp_doc)
        
        log_debug(f"Viewer: Adicionando {num_pages} páginas de {path.name}")
        
        for i in range(num_pages):
            page_widget = PageWidget(path_str, i)
            self.layout.addWidget(page_widget)
            self._pages.append(page_widget)
            
        temp_doc.close()
        self.check_visibility()

    def _initial_render(self):
        self.fit_width()
        self.check_visibility()

    def check_visibility(self):
        """Solicita renderização das páginas que entram no viewport."""
        viewport_top = self.verticalScrollBar().value()
        viewport_bottom = viewport_top + self.height()
        buffer = 1200 
        
        for page in self._pages:
            pos = page.pos().y()
            if pos < viewport_bottom + buffer and pos + page.height() > viewport_top - buffer:
                page.render_page(zoom=self._zoom)

        # Emitir mudança de página se necessário
        current_idx = self.get_current_page_index()
        if current_idx != self._last_emitted_page:
            self._last_emitted_page = current_idx
            self.pageChanged.emit(current_idx)

    def set_zoom(self, zoom: float):
        self._zoom = max(0.1, min(zoom, 10.0))
        self.check_visibility()

    def zoom_in(self): self.set_zoom(self._zoom * 1.2)
    def zoom_out(self): self.set_zoom(self._zoom / 1.2)

    def get_current_page_index(self) -> int:
        """Retorna o índice da página mais visível no topo do viewport."""
        viewport_top = self.verticalScrollBar().value()
        for i, page in enumerate(self._pages):
            # Se o fundo da página estiver abaixo do topo do viewport, ela é a atual
            if page.pos().y() + page.height() > viewport_top + 10:
                return i
        return 0

    def fit_width(self):
        if not self._pages: return
        idx = self.get_current_page_index()
        target_page = self._pages[idx]
        
        # Obter largura original da página específica
        doc = fitz.open(target_page.source_path)
        page_rect = doc[target_page.source_index].rect
        doc.close()

        available_width = self.viewport().width() - 80 # Margens
        self.set_zoom(available_width / page_rect.width)

    def fit_height(self):
        if not self._pages: return
        idx = self.get_current_page_index()
        target_page = self._pages[idx]
        
        doc = fitz.open(target_page.source_path)
        page_rect = doc[target_page.source_index].rect
        doc.close()

        available_height = self.viewport().height() - 80
        self.set_zoom(available_height / page_rect.height)

    def real_size(self): self.set_zoom(1.0)

    def refresh_page(self, visual_idx: int, rotation: int = 0):
        """Força a renderização de uma página específica pela sua posição atual."""
        if 0 <= visual_idx < len(self._pages):
            self._pages[visual_idx].render_page(zoom=self._zoom, rotation=rotation)

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

    def reorder_pages(self, new_order_of_current_widgets: list[int]):
        """Reordena os widgets físicos baseando-se na nova ordem desejada."""
        if not self._pages: return
        
        # Importante: new_order_of_current_widgets contém os índices da lista self._pages
        current_pages = list(self._pages)
        
        for i in reversed(range(self.layout.count())):
            item = self.layout.takeAt(i)
            if item.widget(): item.widget().setParent(None)
        
        self._pages = []
        for idx in new_order_of_current_widgets:
            widget = current_pages[idx]
            self.layout.addWidget(widget)
            self._pages.append(widget)
        
        self.check_visibility()

    def scroll_to_page(self, visual_index: int):
        if 0 <= visual_index < len(self._pages):
            self.verticalScrollBar().setValue(self._pages[visual_index].pos().y())

    def closeEvent(self, event):
        self.clear()
        super().closeEvent(event)
