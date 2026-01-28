from pathlib import Path
from PyQt6.QtWidgets import QScrollArea, QVBoxLayout, QWidget, QFrame, QMenu, QApplication, QRubberBand
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPoint, QEvent, QRect, QRectF
from PyQt6.QtGui import QPainter, QColor, QPalette, QPen, QBrush
from src.interfaces.gui.widgets.page_widget import PageWidget
from src.infrastructure.services.logger import log_debug, log_warning, log_error, log_exception
from src.interfaces.gui.state.render_engine import RenderEngine
from src.interfaces.gui.widgets.floating_navbar import FloatingNavBar
from src.interfaces.gui.widgets.nav_hub import NavHub
from src.interfaces.gui.widgets.marker_scrollbar import MarkerScrollBar


class SelectionOverlay(QWidget):
    """Transparent overlay for painting selection highlights on top of pages."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self._viewer = None # Set by viewer

    def set_viewer_ref(self, viewer):
        self._viewer = viewer

    def paintEvent(self, event):
        if self._viewer:
            painter = QPainter(self)
            self._viewer._draw_selection_highlight(painter)
            painter.end()

class SelectionContainer(QWidget):
    """Container widget that handles layout and overlay resizing."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._overlay = SelectionOverlay(self)
        
    def set_viewer_ref(self, viewer):
        self._overlay.set_viewer_ref(viewer)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._overlay.resize(self.size())
        self._overlay.raise_()


class PDFViewerWidget(QScrollArea):
    """Visualizador que suporta documentos virtuais (múltiplas fontes)."""
    pageChanged = pyqtSignal(int)
    selectionChanged = pyqtSignal(tuple)  # (pdf_x0, pdf_y0, pdf_x1, pdf_y1)
    textExtracted = pyqtSignal(str)  # Texto selecionado extraído
    statusMessageRequested = pyqtSignal(str, int) # (mensagem, timeout_ms)
    draftNoteRequested = pyqtSignal(str) # Solicitação para enviar texto para rascunho de nota

    def __init__(self):
        super().__init__()
        # We don't need event filter anymore with SelectionContainer
        
        self.setWidgetResizable(True)
        self.setWidgetResizable(True)
        # Use custom container for painting
        self.container = SelectionContainer() # Parent set via setWidget implicitly or invalid? better no parent first
        self.container.set_viewer_ref(self)
        
        self.layout = QVBoxLayout(self.container)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.setSpacing(30)
        self.layout.setContentsMargins(40, 40, 40, 40)
        
        self.setWidget(self.container)
        self.container.setStyleSheet("background-color: #1e1e1e;")
        
        # Custom ScrollBar com marcadores
        self.setVerticalScrollBar(MarkerScrollBar(Qt.Orientation.Vertical, self))
        
        # Floating Navigation Bar
        self.nav_bar = FloatingNavBar(self)
        self.nav_bar.hide()
        self._setup_nav_bar_connections()
        
        # Navigation Hub (SteeringWheel)
        self.nav_hub = NavHub(self)
        self.nav_hub.toolChanged.connect(self._on_hub_tool_changed)
        self.nav_hub.hide()
        
        self._pages: list[PageWidget] = []
        self._page_sizes: list[tuple[float, float]] = [] 
        self._zoom = 1.0
        self._mode = "default"
        self._layout_mode = "single"
        self._last_emitted_page = -1
        # Throttling de visibilidade para evitar flood de renderização
        self._visibility_timer = QTimer(self)
        self._visibility_timer.setSingleShot(True)
        self._visibility_timer.timeout.connect(self._do_check_visibility)
        
        # Controle de renderização em lote
        self.verticalScrollBar().valueChanged.connect(self.check_visibility)

        
        # Área de Seleção (OCR/Anotações)
        self._selection_mode = False
        self._selecting = False
        self._selection_start = None
        self._selection_rect = None
        self._selection_overlay = None  # RubberBand for zoom_area only
        
        # Paint-based Text Selection (robust, performant approach)
        # Single unified selection model like Chrome PDF viewer
        self._selected_word_rects = []  # List of current DRAG highlights
        self._persistent_selection = {} # Cache of { (page_idx, word_idx): rect_data }
        self._current_page_words = {}  # Cache: {words: [...], page_pos: QPoint}
        self._selected_text = ""  # Text currently selected
        self._highlight_color = "#3399FF"  # Selection blue
        self._persistent_highlight_color = "#2196F3" # Solid blue for saved selection
        self._selection_is_crossing = False 
        self._current_selection_rect = None 
        self._selection_modifier = Qt.KeyboardModifier.NoModifier
        
        # Tool Mode & Interaction
        # Simplified modes: 'pan', 'selection', 'zoom_area'
        self._tool_mode = "pan"
        self._panning = False
        self._last_mouse_pos = QPoint(0, 0)




    def clear(self):
        """Limpa o visualizador e encerra processos pendentes."""
        RenderEngine.instance().clear_queue()
        if hasattr(self, "_visibility_timer"):
            self._visibility_timer.stop()
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self._pages.clear()
        self._page_sizes.clear()
        self._hints = {}
        self._last_emitted_page = -1

    def setPlaceholder(self, widget: QWidget):
        self.clear()
        self.layout.addWidget(widget)

    def load_document(self, path: Path, metadata: dict):
        """Inicializa o visualizador com um arquivo e seus metadados."""
        #log_debug(f"PDFViewerWidget: load_document chamado para {path.name} (page_count={metadata.get('page_count', 0)})")
        self.clear()
        self._hints = metadata.get("hints", {"complexity": "STANDARD"})
        self.add_pages(path, metadata)

    def add_pages(self, path: Path, metadata: dict):
        """Adiciona páginas de um novo documento de forma progressiva."""
        page_count = metadata.get("page_count", 0)
        page_info = metadata.get("pages", [])
        
        # FALLBACK DE ÚLTIMO RECURSO: Se page_count for 0, tentar abrir o documento diretamente
        # Isso garante que o visualizador exiba o PDF mesmo se a análise de metadados falhou
        if page_count == 0:
            log_warning(f"Viewer: page_count=0 detectado para {path.name}. Tentando fallback direto...")
            try:
                import fitz
                with fitz.open(str(path)) as doc:
                    page_count = doc.page_count
                    # Gerar page_info básico com tamanho A4 padrão
                    page_info = [{"width_mm": 210, "height_mm": 297, "format": "A4"} for _ in range(page_count)]
                log_debug(f"Viewer: Fallback bem-sucedido. Páginas detectadas: {page_count}")
            except Exception as e:
                log_exception(f"Viewer: Fallback de abertura falhou: {e}")
                # Não há como exibir nada, mas não propagamos o erro
                return
        
        # Carregamento Progressivo: carregar as primeiras N páginas imediatamente
        # e as demais em background para garantir abertura < 1s
        initial_batch = 20
        
        def create_page_widgets(start_idx, count):
            if not self.container: return
            self.container.setUpdatesEnabled(False)
            
            end_idx = min(start_idx + count, page_count)
            log_debug(f"Viewer: Batch creation {start_idx} to {end_idx}...")
            
            try:
                for i in range(start_idx, end_idx):
                    try:
                        w_pt, h_pt = 0, 0
                        if i < len(page_info):
                            page_meta = page_info[i]
                            w_pt = page_meta.get("width_pt", 0)
                            h_pt = page_meta.get("height_pt", 0)
                            self._page_sizes.append(page_meta)
                        else:
                            self._page_sizes.append({"width_pt": 595, "height_pt": 842})
                            
                        page_widget = PageWidget(str(path), i, width_pt=w_pt, height_pt=h_pt)
                        self.layout.addWidget(page_widget)
                        self._pages.append(page_widget)
                    except Exception as e:
                        log_error(f"Viewer: Erro ao criar widget da página {i}: {e}")
                
                self.container.setUpdatesEnabled(True)
                
                # Trigger visibility check after first batch to start rendering immediately
                if start_idx == 0 and end_idx > 0:
                    QTimer.singleShot(10, self.check_visibility)
                
                if end_idx < page_count:
                    # Pequeno delay para respirar a GUI
                    QTimer.singleShot(20, lambda: create_page_widgets(end_idx, 20))
                else:
                    log_debug(f"Viewer: Carregamento de {page_count} páginas concluído com sucesso.")
                    # Final visibility check to catch any remaining pages
                    QTimer.singleShot(100, self.check_visibility)
                    
            except Exception as outer_e:
                log_exception(f"Viewer: Erro crítico no lote {start_idx}: {outer_e}")
                
        # Garantir que timers anteriores parem
        if self._visibility_timer.isActive():
            self._visibility_timer.stop()

        create_page_widgets(0, initial_batch)

    def check_visibility(self):
        """Garante que a verificação de visibilidade seja throttled."""
        #log_debug(f"Viewer: check_visibility chamado. Pages: {len(self._pages)}")
        self._visibility_timer.start(100)

    def _do_check_visibility(self):
        """Solicita renderização das páginas que entram no viewport (Execução real)."""
        if not self._pages:
            #log_debug("Viewer: _do_check_visibility - Sem páginas!")
            return
        
        #log_debug(f"Viewer: _do_check_visibility - {len(self._pages)} páginas disponíveis")
        
        scroll_v = self.verticalScrollBar().value()
        viewport_h = self.viewport().height()
        viewport_top = scroll_v
        viewport_bottom = scroll_v + viewport_h
        
        # Otimização: Achar índice inicial aproximado (Binary Search seria ideal, mas heurística linear local é ok)
        # O self.get_current_page_index() já faz uma busca.
        current_idx = self.get_current_page_index()
        
        # Margem de segurança (buffer) baseada na complexidade
        complexity = self._hints.get("complexity", "STANDARD")
        buffer = 800 if complexity in ("HEAVY", "ULTRA_HEAVY") else 400 
        
        # Throttling agressivo para HEAVY: se estiver rodando, pular este ciclo?
        # Por enquanto, mantemos o logic padrão mas com buffers maiores.
        
        for i in range(current_idx, len(self._pages)):
            page = self._pages[i]
            pos_y = page.pos().y()
            page_h = page.height()
            
            # Optimization: Early Exit (Downward)
            if pos_y > viewport_bottom + buffer:
                break
                
            # Se a página está visível (com buffer)
            if pos_y < viewport_bottom + buffer and pos_y + page_h > viewport_top - buffer:
                
                # Inteligência Adaptativa: 
                clip = None
                if complexity in ("HEAVY", "ULTRA_HEAVY"):
                    # Calcular interseção entre viewport e página
                    y0_v = max(0, viewport_top - pos_y)
                    y1_v = min(page_h, viewport_bottom - pos_y)
                    
                    if self._zoom > 0:
                        clip = (0, y0_v / self._zoom, page.width() / self._zoom, y1_v / self._zoom)
                
                # Prioridade: 10 se estiver no viewport central, 0 se for buffer
                priority = 10 if (pos_y < viewport_bottom and pos_y + page_h > viewport_top) else 0
                #log_debug(f"Viewer: Requesting render for page {i} (zoom={self._zoom}, visible)")
                page.render_page(zoom=self._zoom, mode=self._mode, clip=clip, priority=priority)

        # Optimization: Check backward (Upward) for buffer items
        for i in range(current_idx - 1, -1, -1):
            page = self._pages[i]
            pos_y = page.pos().y()
            page_h = page.height()
            
            # Early Exit (Upward)
            if pos_y + page_h < viewport_top - buffer:
                break
                
            if pos_y < viewport_bottom + buffer and pos_y + page_h > viewport_top - buffer:
                page.render_page(zoom=self._zoom, mode=self._mode, priority=0)

        # Emitir mudança de página se necessário
        current_idx = self.get_current_page_index()
        if current_idx != self._last_emitted_page:
            self._last_emitted_page = current_idx
            self.pageChanged.emit(current_idx)
            self.nav_bar.update_page(current_idx, len(self._pages))
            if len(self._pages) > 0:
                self.nav_bar.show()
                # Posicionar a navbar no fundo central
                self._update_nav_pos()

    def get_current_page_index(self) -> int:
        """Retorna o índice da página mais visível no topo do viewport."""
        viewport_top = self.verticalScrollBar().value()
        for i, page in enumerate(self._pages):
            # Se o fundo da página estiver abaixo do topo do viewport, ela é a atual
            if page.pos().y() + page.height() > viewport_top + 10:
                return i
        return 0

    def _setup_nav_bar_connections(self):
        self.nav_bar.zoomIn.connect(self.zoom_in)
        self.nav_bar.zoomOut.connect(self.zoom_out)
        self.nav_bar.resetZoom.connect(self.reset_zoom)
        self.nav_bar.nextPage.connect(self.next_page)
        self.nav_bar.prevPage.connect(self.prev_page)
        self.nav_bar.fitWidth.connect(self.fit_width)
        self.nav_bar.fitHeight.connect(self.fit_height)
        self.nav_bar.fitPage.connect(self.fit_page)
        self.nav_bar.setTool.connect(self.set_tool_mode)
        
        # Conectar Visão Geral à troca de modo na MainWindow (via sinal ou callback)
        try:
            main_window = self.window()
            if hasattr(main_window, "_switch_view_mode_v4"):
                self.nav_bar.viewAll.connect(lambda: main_window._switch_view_mode_v4("table"))
        except: pass

    def set_zoom(self, zoom: float, focus_pos=None):
        old_zoom = self._zoom
        new_zoom = max(0.1, min(zoom, 10.0))
        if abs(old_zoom - new_zoom) < 0.001: return
        
        # Posição do scroll atual
        scroll_x = self.horizontalScrollBar().value()
        scroll_y = self.verticalScrollBar().value()
        
        # Se um ponto de foco foi fornecido (ex: cursor do mouse)
        if focus_pos:
            # Posição relativa ao conteúdo (em escala 1.0 teórica)
            rel_x = (focus_pos.x() + scroll_x) / old_zoom
            rel_y = (focus_pos.y() + scroll_y) / old_zoom
            
            self._zoom = new_zoom
            for page in self._pages:
                page.update_layout_size(self._zoom)
            
            # Forçar atualização de layout do container para que o scrollArea saiba o novo tamanho
            self.container.adjustSize()
            
            # Recalcular scroll para manter o ponto rel_x, rel_y sob o focus_pos
            self.horizontalScrollBar().setValue(int(rel_x * self._zoom - focus_pos.x()))
            self.verticalScrollBar().setValue(int(rel_y * self._zoom - focus_pos.y()))
        else:
            self._zoom = new_zoom
            for page in self._pages:
                page.update_layout_size(self._zoom)
                
        self.check_visibility()

    def zoom_in(self): self.set_zoom(self._zoom * 1.2)
    def zoom_out(self): self.set_zoom(self._zoom / 1.2)
    def reset_zoom(self): self.set_zoom(1.0)

    def next_page(self):
        idx = self.get_current_page_index()
        self.scroll_to_page(idx + 1)

    def prev_page(self):
        idx = self.get_current_page_index()
        self.scroll_to_page(idx - 1)

    def fit_width(self):
        """Ajusta o zoom para que a página ocupe toda a largura disponível."""
        if not self._pages: return
        idx = self.get_current_page_index()
        # Usar dimensões da página atual ou da primeira como fallback
        if idx < len(self._page_sizes):
            orig_w = self._page_sizes[idx].get("width_pt", 595.0)
        else:
            orig_w = 595.0
            
        available_w = self.viewport().width() - 100
        self.set_zoom(available_w / orig_w)

    def fit_page(self):
        """Ajusta o zoom para que a página caiba inteira no viewport vertical."""
        if not self._pages: return
        idx = self.get_current_page_index()
        if idx < len(self._page_sizes):
            orig_h = self._page_sizes[idx].get("height_pt", 842.0)
        else:
            orig_h = 842.0
            
        available_h = self.viewport().height() - 100
        self.set_zoom(available_h / orig_h)

    def fit_height(self):
        """Ajusta o zoom para que a altura da página ocupe todo o viewport."""
        if not self._pages: return
        idx = self.get_current_page_index()
        if idx < len(self._page_sizes):
            orig_h = self._page_sizes[idx].get("height_pt", 842.0)
        else:
            orig_h = 842.0
        
        available_h = self.viewport().height() - 40
        self.set_zoom(available_h / orig_h)

    def keyPressEvent(self, event):
        """Atalhos universais estilo Okular."""
        key = event.key()
        mod = event.modifiers()
        
        if mod == Qt.KeyboardModifier.NoModifier:
            if key == Qt.Key.Key_Space or key == Qt.Key.Key_PageDown:
                self.next_page()
            elif key == Qt.Key.Key_Backspace or key == Qt.Key.Key_PageUp:
                self.prev_page()
            elif key == Qt.Key.Key_P:
                self.set_tool_mode("pan")
            elif key == Qt.Key.Key_S:
                # S = Selection mode (unified text selection)
                self.set_tool_mode("selection")
            elif key == Qt.Key.Key_Z:
                self.set_tool_mode("zoom_area")
            elif key == Qt.Key.Key_N:
                # Toggle NavHub
                if self.nav_hub.isVisible(): self.nav_hub.hide()
                else: self.nav_hub.show()
                self._update_nav_pos()
            else:
                super().keyPressEvent(event)
        
        elif mod == Qt.KeyboardModifier.ControlModifier:
            if key == Qt.Key.Key_Plus or key == Qt.Key.Key_Equal: self.zoom_in()
            elif key == Qt.Key.Key_Minus: self.zoom_out()
            elif key == Qt.Key.Key_0: self.reset_zoom()
            elif key == Qt.Key.Key_1: self.fit_width()
            elif key == Qt.Key.Key_2: self.fit_page()
            else: super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)




    def _on_hub_tool_changed(self, action):
        if action == "pan": self.set_tool_mode("pan")
        elif action == "select": self.set_tool_mode("selection")
        elif action == "zoom_in": self.zoom_in()
        elif action == "zoom_out": self.zoom_out()
        elif action == "fit_width": self.fit_width()
        elif action == "fit_page": self.fit_page()

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

    selectionChanged = pyqtSignal(tuple) # (x0, y0, x1, y1) em pontos PDF

    def refresh_current_view(self):
        """Força a renderização das páginas no viewport (usado após mudar visibilidade de layers)."""
        for page in self._pages:
            page.render_page(zoom=self._zoom, mode=self._mode, force=True)

    def set_tool_mode(self, mode: str):
        """Alterna entre 'pan', 'selection' e 'zoom_area'."""
        # Backwards compatibility
        if mode in ("selection_flow", "selection_area"):
            mode = "selection"
        
        self._tool_mode = mode
        if hasattr(self, 'nav_hub'):
            self.nav_hub.set_tool(mode)
            
        if mode == "selection":
            self.setCursor(Qt.CursorShape.IBeamCursor)
            self.statusMessageRequested.emit("Modo Seleção Ativo: Selecione texto para copiar.", 3000)
        elif mode == "zoom_area":
            self.setCursor(Qt.CursorShape.CrossCursor)
            self.statusMessageRequested.emit("Modo Zoom: Selecione uma área para ampliar.", 3000)
        else:
            self.setCursor(Qt.CursorShape.OpenHandCursor)
            self.statusMessageRequested.emit("Modo Pan: Arraste para mover.", 2000)
            
        self._clear_selection()


    def set_highlight_color(self, color: str):
        """Sets the highlight color for annotations."""
        self._highlight_color = color
        log_debug(f"Highlight color set to: {color}")


    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_nav_pos()

    def _update_nav_pos(self):
        # NavBar centralizada no topo
        if hasattr(self, "nav_bar") and self.nav_bar.isVisible():
            self.nav_bar.move((self.width() - self.nav_bar.width()) // 2, 20)
        # NavHub centralizado na base
        if hasattr(self, "nav_hub") and self.nav_hub.isVisible():
            self.nav_hub.move((self.width() - self.nav_hub.width()) // 2, self.height() - 80)


    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            super().mousePressEvent(event)
            return
            
        # Map mouse events to container coordinates (handles scroll automatically)
        container_pos = self.container.mapFrom(self, event.position().toPoint())
            
        if self._tool_mode == "zoom_area":
            self._selecting = True
            # For RubberBand we usually use global/viewport coords, but let's stick to standard behavior
            self._selection_start = event.position().toPoint()
            if not self._selection_overlay:
                self._selection_overlay = QRubberBand(QRubberBand.Shape.Rectangle, self)
            self._selection_overlay.setGeometry(self._selection_start.x(), self._selection_start.y(), 0, 0)
            self._selection_overlay.show()
            
        elif self._tool_mode == "selection":
            self._selecting = True
            self._selection_start = container_pos
            self._selected_word_rects = []
            self._selection_modifier = event.modifiers()
            
            # If no modifier, clear previous selection
            if self._selection_modifier == Qt.KeyboardModifier.NoModifier:
                self._persistent_selection = {}
                
            self._cache_page_words_at_point(container_pos)
            self.container._overlay.update()
            
        elif self._tool_mode == "pan":
            self._panning = True
            self._last_mouse_pos = event.position().toPoint()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            
        super().mousePressEvent(event)


    def mouseReleaseEvent(self, event):
        if self._selecting:
            self._selecting = False
            
            if self._tool_mode == "zoom_area":
                end_pos = event.position().toPoint()
                self._apply_zoom_to_selection(self._selection_start, end_pos)
                self._clear_selection()
                
            elif self._tool_mode == "selection":
                container_pos = self.container.mapFrom(self, event.position().toPoint())
                self._apply_drag_to_persistent()
                self._finalize_selection(container_pos)
                if self._selected_text:
                    self._show_context_menu(event.globalPosition().toPoint())
                # Note: We keep persistent selection visible. 
                # To clear, the user clicks without modifiers.
        
        self._panning = False
        
        if self._tool_mode == "selection":
            self.setCursor(Qt.CursorShape.IBeamCursor)
        elif self._tool_mode == "zoom_area":
            self.setCursor(Qt.CursorShape.CrossCursor)
        else:
            self.setCursor(Qt.CursorShape.OpenHandCursor)
            
        super().mouseReleaseEvent(event)




    def _apply_zoom_to_selection(self, start: QPoint, end: QPoint):
        """Calcula e aplica o zoom para que a área selecionada caiba no viewport."""
        # Dimensões da seleção
        sel_w = abs(end.x() - start.x())
        sel_h = abs(end.y() - start.y())
        
        if sel_w < 20 or sel_h < 20:
            return  # Seleção muito pequena, ignorar
        
        # Centro da seleção (coordenadas do widget)
        center_x = (start.x() + end.x()) // 2
        center_y = (start.y() + end.y()) // 2
        
        # Dimensões do viewport
        vp_w = self.viewport().width()
        vp_h = self.viewport().height()
        
        # Fator de zoom necessário para encaixar a seleção
        zoom_factor_w = vp_w / sel_w
        zoom_factor_h = vp_h / sel_h
        zoom_factor = min(zoom_factor_w, zoom_factor_h) * 0.9  # 90% para margem
        
        # Novo zoom = zoom_atual * fator
        new_zoom = self._zoom * zoom_factor
        new_zoom = max(0.1, min(new_zoom, 10.0))
        
        # Aplicar zoom focado no centro da seleção
        self.set_zoom(new_zoom, focus_pos=QPoint(center_x, center_y))
        
        # Retornar para modo Pan após o zoom
        self.set_tool_mode("pan")



    def _draw_selection_highlight(self, painter):
        """Paint selected word rectangles and the selection box (AutoCAD style)."""
        # 1. Draw Persistent Selection (already selected words)
        if self._persistent_selection:
            color = QColor(self._persistent_highlight_color)
            color.setAlpha(100) # Semi-transparent blue
            painter.setBrush(color)
            painter.setPen(Qt.PenStyle.NoPen)
            for rect_tuple in self._persistent_selection.values():
                painter.drawRect(*rect_tuple)

        # 2. Draw Current Drag (pending selection)
        if self._selected_word_rects:
            # Shift = Additive (Cyan/Green-ish highlight)
            # Ctrl = Subtractive (Red-ish highlight)
            # No Modifier = Standard (Same as persistent but pulsing/different alpha)
            if self._selection_modifier & Qt.KeyboardModifier.ShiftModifier:
                color = QColor(0, 255, 150, 80) # Additive
            elif self._selection_modifier & Qt.KeyboardModifier.ControlModifier:
                color = QColor(255, 80, 80, 10) # Subtractive (Faint red)
            else:
                color = QColor(self._highlight_color)
                color.setAlpha(130)

            painter.setBrush(color)
            # Add a subtle border to pending selection for clarity
            pen = QPen(color.lighter(150), 1)
            painter.setPen(pen)
            
            for rect_tuple in self._selected_word_rects:
                painter.drawRect(*rect_tuple)

        # 3. Draw the Selection Box (RubberBand)
        if self._selecting and self._tool_mode == "selection" and self._current_selection_rect:
            if self._selection_is_crossing:
                box_color = QColor(0, 255, 100, 30) # Green Crossing
                border_color = QColor(0, 255, 100, 150)
            else:
                box_color = QColor(0, 120, 255, 30) # Blue Window
                border_color = QColor(0, 120, 255, 150)
            
            painter.setBrush(box_color)
            pen = QPen(border_color, 1, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.drawRect(self._current_selection_rect)

    def _finalize_selection(self, end_pos: QPoint):
        """Extracts text from all selected words in persistent selection."""
        if not self._persistent_selection:
            self._selected_text = ""
            return
            
        try:
            from src.infrastructure.adapters.pymupdf_adapter import PyMuPDFAdapter
            all_text_fragments = []
            
            # Group by page to minimize adapter calls
            selection_by_page = {}
            for (p_idx, w_idx), rect in self._persistent_selection.items():
                if p_idx not in selection_by_page: selection_by_page[p_idx] = []
                selection_by_page[p_idx].append(w_idx)
            
            for p_idx in sorted(selection_by_page.keys()):
                page_widget = self._pages[p_idx]
                words = PyMuPDFAdapter.get_text(str(page_widget.source_path), page_widget.source_index, "words")
                
                # Sort indices for this page to maintain reading order
                indices = sorted(selection_by_page[p_idx])
                all_text_fragments.extend([words[i][4] for i in indices])
            
            if all_text_fragments:
                self._selected_text = " ".join(all_text_fragments)
                # Removed Auto-Copy
                # QApplication.clipboard().setText(self._selected_text) 
                
                self.textExtracted.emit(self._selected_text)
                log_debug(f"Selection finalized: {len(self._selected_text)} chars")
                self.statusMessageRequested.emit(f"Seleção: {len(self._selected_text)} caracteres. Escolha uma ação.", 0)
                
                # Trigger Menu Immediately
                from PyQt6.QtGui import QCursor
                QTimer.singleShot(50, lambda: self._show_context_menu(QCursor.pos()))
            else:
                self._selected_text = ""
                
        except Exception as e:
            log_error(f"Selection extraction error: {e}")
            self._selected_text = ""

    def _clear_selection(self):
        """Unified selection clearing for all modes."""
        self._selecting = False
        if self._selection_overlay:
            self._selection_overlay.hide()
        self._selected_word_rects = []
        self._persistent_selection = {} # Clear persistent too!
        self._selected_text = ""
        self.container._overlay.update() # Force repaint SelectionOverlay


    def _show_context_menu(self, pos: QPoint):
        menu = QMenu(self)
        menu.setStyleSheet("QMenu { background-color: #252526; color: #CCCCCC; border: 1px solid #454545; padding: 5px; } QMenu::item { padding: 5px 20px; } QMenu::item:selected { background-color: #37373d; }")
        
        # Info Header
        info_action = menu.addAction(f"{len(self._selected_text)} caracteres")
        info_action.setEnabled(False)
        menu.addSeparator()
        
        copy_action = menu.addAction("📋 Copiar Texto")
        highlight_action = menu.addAction("🖍️ Realçar")
        note_action = menu.addAction("📝 Criar Nota (Draft)")
        
        menu.addSeparator()
        clear_action = menu.addAction("❌ Limpar Seleção")
        
        action = menu.exec(pos)
        
        if action == copy_action:
            QApplication.clipboard().setText(self._selected_text)
            self.statusMessageRequested.emit("Texto copiado para a área de transferência.", 2000)
            self._clear_selection()
            
        elif action == highlight_action:
            # TODO: Integrate with actual Annotation/Highlight logic
            log_debug("Context Menu: Highlight triggered")
            # For now, keep the selection visible to simulate highlight persistence until cleared
            self.statusMessageRequested.emit("Texto marcado (Mock - funcionalidade futura).", 2000)
            # self._clear_selection() # Keep selection for verify
            
        elif action == note_action:
            self.draftNoteRequested.emit(self._selected_text)
            self.statusMessageRequested.emit("Texto enviado para painel de notas.", 2000)
            # self._clear_selection() # Keep selection so user sees what they drafted
            
        elif action == clear_action:
            self._clear_selection()

    def mouseMoveEvent(self, event):
        if self._selecting:
            # Update RubberBand if active for zoom_area
            if self._selection_overlay and self._tool_mode == "zoom_area":
                self._selection_overlay.setGeometry(
                    int(min(self._selection_start.x(), event.position().x())),
                    int(min(self._selection_start.y(), event.position().y())),
                    int(abs(self._selection_start.x() - event.position().x())),
                    int(abs(self._selection_start.y() - event.position().y()))
                )
            
            # Efficient paint-based selection
            elif self._tool_mode == "selection":
                container_pos = self.container.mapFrom(self, event.position().toPoint())
                self._update_selection_rects(container_pos)
                self.container._overlay.update() # Trigger paint on SelectionOverlay

        elif self._panning:
            delta = event.position().toPoint() - self._last_mouse_pos
            self._last_mouse_pos = event.position().toPoint()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
        super().mouseMoveEvent(event)

    def _clear_selection(self):
        """Unified selection clearing for all modes."""
        self._selecting = False
        if self._selection_overlay:
            self._selection_overlay.hide()
        self._selected_word_rects = []
        self._selected_text = ""
        self.container.update() # Force repaint SelectionContainer

    def _update_selection_rects(self, current_pos: QPoint):
        """Calculates selection rectangles calling container coordinates."""
        try:
            self._selected_word_rects = []
            self._current_drag_ids = [] # (page_idx, word_idx)
            
            if not self._current_page_words or not self._current_page_words.get("words"):
                return
            
            self._selection_is_crossing = current_pos.x() >= self._selection_start.x()
            # Normalize to ensure valid positive dimensions
            self._current_selection_rect = QRect(self._selection_start, current_pos).normalized()
            
            words = self._current_page_words["words"]
            page_pos = self._current_page_words["page_pos"]
            page_idx = self._current_page_words["page_index"]
            
            # Debug: Print container and page coordinates
            # log_debug(f"Selection Rect (Container): {self._current_selection_rect}")
            # log_debug(f"Page Pos: {page_pos}")
            
            sel_x0 = (self._current_selection_rect.left() - page_pos.x()) / self._zoom
            sel_y0 = (self._current_selection_rect.top() - page_pos.y()) / self._zoom
            sel_x1 = (self._current_selection_rect.right() - page_pos.x()) / self._zoom
            sel_y1 = (self._current_selection_rect.bottom() - page_pos.y()) / self._zoom
            
            # Debug: Print PDF coordinates
            # log_debug(f"Selection Rect (PDF Points): {sel_x0}, {sel_y0} -> {sel_x1}, {sel_y1}")

            for i, word_data in enumerate(words):
                x0, y0, x1, y1 = word_data[:4]
                
                is_selected = False
                if self._selection_is_crossing:
                    is_selected = not (x1 < sel_x0 or x0 > sel_x1 or y1 < sel_y0 or y0 > sel_y1)
                else:
                    is_selected = (x0 >= sel_x0 and x1 <= sel_x1 and y0 >= sel_y0 and y1 <= sel_y1)
                
                if is_selected:
                    rect_x = int(x0 * self._zoom + page_pos.x())
                    rect_y = int(y0 * self._zoom + page_pos.y())
                    rect_w = int((x1 - x0) * self._zoom)
                    rect_h = int((y1 - y0) * self._zoom)
                    
                    self._selected_word_rects.append((rect_x, rect_y, rect_w, rect_h))
                    self._current_drag_ids.append((page_idx, i, (rect_x, rect_y, rect_w, rect_h)))
                    
            mode_text = "Crossing (L->R)" if self._selection_is_crossing else "Window (R->L)"
            mod_text = " [+]" if self._selection_modifier & Qt.KeyboardModifier.ShiftModifier else \
                       " [-]" if self._selection_modifier & Qt.KeyboardModifier.ControlModifier else ""
            self.statusMessageRequested.emit(f"Seleção {mode_text}{mod_text}: {len(self._selected_word_rects)} palavras", 0)
                    
        except Exception as e:
            log_error(f"Error updating selection: {e}")

    def _apply_drag_to_persistent(self):
        """Merges or subtracts the current drag into the persistent selection."""
        if not hasattr(self, "_current_drag_ids"):
            return

        if self._selection_modifier & Qt.KeyboardModifier.ShiftModifier:
            # Additive
            for page_idx, word_idx, rect in self._current_drag_ids:
                self._persistent_selection[(page_idx, word_idx)] = rect
        elif self._selection_modifier & Qt.KeyboardModifier.ControlModifier:
            # Subtractive
            for page_idx, word_idx, _ in self._current_drag_ids:
                if (page_idx, word_idx) in self._persistent_selection:
                    del self._persistent_selection[(page_idx, word_idx)]
        else:
            # Overwrite
            self._persistent_selection = {}
            for page_idx, word_idx, rect in self._current_drag_ids:
                self._persistent_selection[(page_idx, word_idx)] = rect
        
        self._selected_word_rects = [] # Clear current drag view
        self._current_selection_rect = None

    def _cache_page_words_at_point(self, pos: QPoint):
        """Identifies page under cursor (container coords) and caches words."""
        try:
            from src.infrastructure.adapters.pymupdf_adapter import PyMuPDFAdapter
            
            self._current_page_words = {}
            
            for i, page in enumerate(self._pages):
                if page.geometry().contains(pos):
                    log_debug(f"Selection start on page {i+1}")
                    words = PyMuPDFAdapter.get_text(str(page.source_path), page.source_index, "words")
                    
                    self._current_page_words = {
                        "words": words,
                        "page_pos": page.pos(), # Container pos
                        "page_index": i
                    }
                    return
            
            log_debug("Selection started outside any page")
            
        except Exception as e:
            log_error(f"Failed to cache words: {e}")






    def wheelEvent(self, event):

        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            factor = 1.2 if event.angleDelta().y() > 0 else 1.0 / 1.2
            self.set_zoom(self._zoom * factor, focus_pos=event.position())
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

    def scroll_to_page(self, visual_index: int, highlights: list = None):
        if 0 <= visual_index < len(self._pages):
            y = self._pages[visual_index].pos().y()
            self.verticalScrollBar().setValue(y)
            
            if highlights:
                page = self._pages[visual_index]
                page.set_highlights(highlights)
                # Limpar após 2 segundos (efeito temporário estilo VS Code)
                QTimer.singleShot(2000, lambda: page.set_highlights([]))

    def closeEvent(self, event):
        self.clear()
        super().closeEvent(event)
