from pathlib import Path
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
        self.container = QWidget()
        self.layout = QVBoxLayout(self.container)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.setSpacing(30)
        self.layout.setContentsMargins(40, 40, 40, 40)
        
        self.setWidget(self.container)
        self.container.setStyleSheet("background-color: #1e1e1e;")
        
        self._pages: list[PageWidget] = []
        self._page_sizes: list[tuple[float, float]] = [] # Armazena (w, h) de cada página original
        self._zoom = 1.0
        self._mode = "default"
        self._layout_mode = "single"
        self._last_emitted_page = -1

        # Controle de renderização em lote
        self.verticalScrollBar().valueChanged.connect(self.check_visibility)
        
        # Área de Seleção (OCR/Anotações)
        self._selection_mode = False
        self._selecting = False
        self._selection_start = None
        self._selection_rect = None
        self._selection_overlay = None

    def clear(self):
        """Limpa o visualizador e encerra processos pendentes."""
        RenderEngine.instance().clear_queue()
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self._pages.clear()
        self._page_sizes.clear()
        self._last_emitted_page = -1

    def setPlaceholder(self, widget: QWidget):
        self.clear()
        self.layout.addWidget(widget)

    def load_document(self, path: Path, metadata: dict):
        """Inicializa o visualizador com um arquivo e seus metadados."""
        self.clear()
        self.add_pages(path, metadata)

    def add_pages(self, path: Path, metadata: dict):
        """Adiciona páginas de um novo documento sem resetar."""
        page_count = metadata.get("page_count", 0)
        page_info = metadata.get("pages", [])
        
        for i in range(page_count):
            page_widget = PageWidget(str(path), i)
            self.layout.addWidget(page_widget)
            self._pages.append(page_widget)
            
            # Armazenar tamanho original para cálculos de zoom/fit
            if i < len(page_info):
                self._page_sizes.append(page_info[i])
            else:
                self._page_sizes.append((595.0, 842.0)) # Fallback A4
        
        QTimer.singleShot(100, self._initial_render)

    def _initial_render(self):
        self.check_visibility()

    def check_visibility(self):
        """Solicita renderização das páginas que entram no viewport."""
        viewport_top = self.verticalScrollBar().value()
        viewport_bottom = viewport_top + self.viewport().height()
        
        # Margem de segurança (buffer) para carregar páginas um pouco antes de entrarem
        buffer = 1200 
        
        for page in self._pages:
            pos = page.pos().y()
            if pos < viewport_bottom + buffer and pos + page.height() > viewport_top - buffer:
                page.render_page(zoom=self._zoom, mode=self._mode)

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
        
        if idx < len(self._page_sizes):
            orig_w, _ = self._page_sizes[idx]
        else:
            orig_w = 595.0

        available_width = self.viewport().width() - 80 # Margens
        self.set_zoom(available_width / orig_w)

    def fit_height(self):
        if not self._pages: return
        idx = self.get_current_page_index()
        
        if idx < len(self._page_sizes):
            _, orig_h = self._page_sizes[idx]
        else:
            orig_h = 842.0

        available_height = self.viewport().height() - 80
        self.set_zoom(available_height / orig_h)

    def real_size(self): self.set_zoom(1.0)

    def refresh_page(self, visual_idx: int, rotation: int = 0):
        """Força a renderização de uma página específica pela sua posição atual."""
        if 0 <= visual_idx < len(self._pages):
            self._pages[visual_idx].render_page(zoom=self._zoom, rotation=rotation, mode=self._mode)

    def set_reading_mode(self, mode: str):
        """Redetalha todas as páginas com o novo filtro de cor."""
        if self._mode == mode: return
        self._mode = mode
        log_debug(f"Viewer: Alterando modo de leitura para {mode}")
        
        # Atualizar cor de fundo do container baseado no modo
        bg_colors = {
            "default": "#1e1e1e",
            "dark": "#0B0F19",
            "sepia": "#F4ECD8",
            "night": "#050505"
        }
        self.container.setStyleSheet(f"background-color: {bg_colors.get(mode, '#1e1e1e')};")
        
        for page in self._pages:
            page.render_page(mode=self._mode)

    def set_layout_mode(self, mode: str):
        """Altera o layout entre página única ou lado-a-lado."""
        if self._layout_mode == mode: return
        self._layout_mode = mode
        log_debug(f"Viewer: Alterando layout para {mode}")
        
        # Desconectar para evitar loops durante re-layout
        try:
            self.verticalScrollBar().valueChanged.disconnect(self.check_visibility)
        except Exception:
            pass
        
        if mode == "dual":
            # Grid layout com 2 colunas
            from PyQt6.QtWidgets import QGridLayout
            new_layout = QGridLayout(self.container)
            new_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            new_layout.setSpacing(30)
            new_layout.setContentsMargins(40, 40, 40, 40)
            
            for i, page in enumerate(self._pages):
                new_layout.addWidget(page, i // 2, i % 2)
        else:
            # Vertical layout padrão
            new_layout = QVBoxLayout(self.container)
            new_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            new_layout.setSpacing(30)
            new_layout.setContentsMargins(40, 40, 40, 40)
            
            for page in self._pages:
                new_layout.addWidget(page)

        # Trocar o layout antigo pelo novo
        old_layout = self.layout
        self.layout = new_layout
        
        # No PyQt6, para trocar o layout, precisamos deletar o antigo
        import sip
        if old_layout:
            sip.delete(old_layout)
        
        self.container.setLayout(new_layout)
        self.verticalScrollBar().valueChanged.connect(self.check_visibility)
        self.check_visibility()

    areaSelected = pyqtSignal(int, tuple) # page_index, (x0, y0, x1, y1) em pontos PDF

    def set_selection_mode(self, enabled: bool):
        self._selection_mode = enabled
        self.setCursor(Qt.CursorShape.CrossCursor if enabled else Qt.CursorShape.ArrowCursor)
        if not enabled:
            self._clear_selection()

    def _clear_selection(self):
        self._selecting = False
        if self._selection_overlay:
            self._selection_overlay.hide()

    def mousePressEvent(self, event):
        if self._selection_mode and event.button() == Qt.MouseButton.LeftButton:
            self._selecting = True
            self._selection_start = event.position().toPoint()
            if not self._selection_overlay:
                from PyQt6.QtWidgets import QRubberBand
                self._selection_overlay = QRubberBand(QRubberBand.Shape.Rectangle, self)
            self._selection_overlay.setGeometry(self._selection_start.x(), self._selection_start.y(), 0, 0)
            self._selection_overlay.show()
        elif event.button() == Qt.MouseButton.LeftButton:
            self._panning = True
            self._last_mouse_pos = event.position().toPoint()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if self._selecting:
            self._selecting = False
            end_pos = event.position().toPoint()
            self._process_selection(self._selection_start, end_pos)
            # Mantém o RubberBand visível por um momento ou limpa
            QTimer.singleShot(500, self._clear_selection)
        
        self._panning = False
        if not self._selection_mode:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if self._selecting:
            self._selection_overlay.setGeometry(
                min(self._selection_start.x(), event.position().x()),
                min(self._selection_start.y(), event.position().y()),
                abs(self._selection_start.x() - event.position().x()),
                abs(self._selection_start.y() - event.position().y())
            )
        elif self._panning:
            delta = event.position().toPoint() - self._last_mouse_pos
            self._last_mouse_pos = event.position().toPoint()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
        super().mouseMoveEvent(event)

    def _process_selection(self, start, end):
        """Converte as coordenadas da tela para as coordenadas do PDF e emite o sinal."""
        # Achar em qual página o clique começou
        viewport_offset = self.verticalScrollBar().value()
        start_y_absolute = start.y() + viewport_offset
        
        for i, page in enumerate(self._pages):
            page_pos = page.pos()
            if page_pos.y() <= start_y_absolute <= page_pos.y() + page.height():
                # Encontrou a página
                # Converter coordenadas locais do widget para pontos do PDF (72 DPI)
                # Levando em conta o Zoom e a margem do container
                local_x = start.x() - page_pos.x()
                local_y = start_y_absolute - page_pos.y()
                
                # Coordenadas de fim relativas à mesma página
                local_x_end = end.x() - page_pos.x()
                local_y_end = end.y() + viewport_offset - page_pos.y()
                
                # Normalizar zoom
                pdf_x0 = min(local_x, local_x_end) / self._zoom
                pdf_y0 = min(local_y, local_y_end) / self._zoom
                pdf_x1 = max(local_x, local_x_end) / self._zoom
                pdf_y1 = max(local_y, local_y_end) / self._zoom
                
                self.areaSelected.emit(i, (pdf_x0, pdf_y0, pdf_x1, pdf_y1))
                break

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
