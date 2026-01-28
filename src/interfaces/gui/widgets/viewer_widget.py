from pathlib import Path
from PyQt6.QtWidgets import QScrollArea, QVBoxLayout, QWidget, QFrame, QMenu, QApplication, QRubberBand
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPoint
from src.interfaces.gui.widgets.page_widget import PageWidget
from src.infrastructure.services.logger import log_debug, log_warning, log_error, log_exception
from src.interfaces.gui.state.render_engine import RenderEngine
from src.interfaces.gui.widgets.floating_navbar import FloatingNavBar
from src.interfaces.gui.widgets.nav_hub import NavHub
from src.interfaces.gui.widgets.marker_scrollbar import MarkerScrollBar

class PDFViewerWidget(QScrollArea):
    """Visualizador que suporta documentos virtuais (múltiplas fontes)."""
    pageChanged = pyqtSignal(int)
    selectionChanged = pyqtSignal(tuple)  # (pdf_x0, pdf_y0, pdf_x1, pdf_y1)
    textExtracted = pyqtSignal(str)  # Texto selecionado extraído

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
        self._selection_overlay = None
        
        # Flow Selection (word-by-word like text editors)
        self._flow_selection_words = []  # List of word rects being selected
        self._flow_start_word = None  # First word index
        self._current_page_words = {}  # Cache: {page_index: [(x0,y0,x1,y1,word,block,line,word_n)...]}
        self._word_highlight_overlays = []  # List of QLabel widgets for word highlights
        self._highlight_color = "#FFEB3B"  # Default highlight color (yellow)
        
        # Tool Mode & Interaction
        # Modes: 'pan', 'selection_flow', 'selection_area', 'zoom_area'
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
                # S = Flow Selection (text editor style)
                self.set_tool_mode("selection_flow")
            elif key == Qt.Key.Key_A:
                # A = Area Selection (CAD style)
                self.set_tool_mode("selection_area")
            elif key == Qt.Key.Key_Z:
                self.set_tool_mode("zoom_area")
            elif key == Qt.Key.Key_N:
                # Toggle NavHub
                if self.nav_hub.isVisible(): self.nav_hub.hide()
                else: self.nav_hub.show()
                self._update_nav_pos()
            else:
                super().keyPressEvent(event)
        
        elif mod == Qt.KeyboardModifier.ShiftModifier:
            if key == Qt.Key.Key_S:
                # Shift+S = Area Selection (CAD style)
                self.set_tool_mode("selection_area")
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
        """Alterna entre 'pan', 'selection_flow', 'selection_area' e 'zoom_area'."""
        # Backwards compatibility: 'selection' maps to 'selection_flow'
        if mode == "selection":
            mode = "selection_flow"
        
        self._tool_mode = mode
        if hasattr(self, 'nav_hub'):
            self.nav_hub.set_tool(mode)
            
        if mode == "selection_flow":
            self.setCursor(Qt.CursorShape.IBeamCursor)
        elif mode == "selection_area":
            self.setCursor(Qt.CursorShape.CrossCursor)
        elif mode == "zoom_area":
            self.setCursor(Qt.CursorShape.CrossCursor)
        else:
            self.setCursor(Qt.CursorShape.OpenHandCursor)

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

    def set_selection_mode(self, enabled: bool):
        # Legado para OCR de área
        self._selection_mode = enabled
        self.setCursor(Qt.CursorShape.CrossCursor if enabled else Qt.CursorShape.ArrowCursor)
        if not enabled:
            self._clear_selection()

    def _clear_selection(self):
        self._selecting = False
        if self._selection_overlay:
            self._selection_overlay.hide()
        # Also clear word highlights
        self._clear_word_highlights()


    def mousePressEvent(self, event):
        if self._selection_mode and event.button() == Qt.MouseButton.LeftButton:
            self._selecting = True
            self._selection_start = event.position().toPoint()
            if not self._selection_overlay:
                from PyQt6.QtWidgets import QRubberBand
                self._selection_overlay = QRubberBand(QRubberBand.Shape.Rectangle, self)
            self._selection_overlay.setGeometry(self._selection_start.x(), self._selection_start.y(), 0, 0)
            self._selection_overlay.show()
        elif self._tool_mode == "zoom_area" and event.button() == Qt.MouseButton.LeftButton:
            # RubberBand para Zoom por Área
            self._selecting = True
            self._selection_start = event.position().toPoint()
            if not self._selection_overlay:
                from PyQt6.QtWidgets import QRubberBand
                self._selection_overlay = QRubberBand(QRubberBand.Shape.Rectangle, self)
            self._selection_overlay.setGeometry(self._selection_start.x(), self._selection_start.y(), 0, 0)
            self._selection_overlay.show()
        elif self._tool_mode == "selection_area" and event.button() == Qt.MouseButton.LeftButton:
            # CAD-style: RubberBand para seleção por área
            self._selecting = True
            self._selection_start = event.position().toPoint()
            if not self._selection_overlay:
                from PyQt6.QtWidgets import QRubberBand
                self._selection_overlay = QRubberBand(QRubberBand.Shape.Rectangle, self)
            self._selection_overlay.setGeometry(self._selection_start.x(), self._selection_start.y(), 0, 0)
            self._selection_overlay.show()
        elif self._tool_mode == "selection_flow" and event.button() == Qt.MouseButton.LeftButton:
            # Text editor style: word-by-word selection (NO RubberBand, only word highlights)
            self._selecting = True
            self._selection_start = event.position().toPoint()
            self._flow_selection_words = []
            # Cache words from the current page for fast lookup
            self._cache_page_words_at_point(self._selection_start)


        elif self._tool_mode == "pan" and event.button() == Qt.MouseButton.LeftButton:
            self._panning = True
            self._last_mouse_pos = event.position().toPoint()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
        super().mousePressEvent(event)


    def mouseReleaseEvent(self, event):
        if self._selecting:
            self._selecting = False
            end_pos = event.position().toPoint()
            
            # Zoom por Área: calcular zoom para encaixar a seleção no viewport
            if self._tool_mode == "zoom_area":
                self._apply_zoom_to_selection(self._selection_start, end_pos)
                self._clear_selection()
            # CAD-style area selection
            elif self._tool_mode == "selection_area":
                self._process_selection(self._selection_start, end_pos)
                self._show_context_menu(event.globalPosition().toPoint())
                QTimer.singleShot(500, self._clear_selection)
            # Text editor flow selection
            elif self._tool_mode == "selection_flow":
                self._process_flow_selection(end_pos)
                self._show_context_menu(event.globalPosition().toPoint())
                QTimer.singleShot(500, self._clear_selection)

            else:
                self._process_selection(self._selection_start, end_pos)
                QTimer.singleShot(500, self._clear_selection)
        
        self._panning = False
        if self._tool_mode == "selection_flow":
            self.setCursor(Qt.CursorShape.IBeamCursor)
        elif self._tool_mode in ("selection_area", "zoom_area"):
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

    def _show_context_menu(self, pos: QPoint):
        menu = QMenu(self)
        menu.setStyleSheet("QMenu { background-color: #252526; color: #CCCCCC; border: 1px solid #454545; }")
        
        copy_action = menu.addAction("📋 Copiar")
        highlight_action = menu.addAction("🖍️ Realçar")
        search_action = menu.addAction("🔍 Pesquisar")
        
        action = menu.exec(pos)
        if action == copy_action:
            log_debug("Context Menu: Copy triggered")
            # TODO: Integrate with clipboard
        elif action == highlight_action:
            log_debug("Context Menu: Highlight triggered")
        elif action == search_action:
            log_debug("Context Menu: Search triggered")

    def mouseMoveEvent(self, event):
        if self._selecting:
            # Update RubberBand for visual feedback
            if self._selection_overlay:
                self._selection_overlay.setGeometry(
                    int(min(self._selection_start.x(), event.position().x())),
                    int(min(self._selection_start.y(), event.position().y())),
                    int(abs(self._selection_start.x() - event.position().x())),
                    int(abs(self._selection_start.y() - event.position().y()))
                )
            
            # For flow selection, also highlight individual words
            if self._tool_mode == "selection_flow" and self._current_page_words:
                self._update_word_highlights(event.position().toPoint())

        elif self._panning:
            delta = event.position().toPoint() - self._last_mouse_pos
            self._last_mouse_pos = event.position().toPoint()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
        super().mouseMoveEvent(event)

    def _update_word_highlights(self, current_pos: QPoint):
        """Updates word highlight overlays during selection drag."""
        try:
            # Clear existing highlights
            for overlay in self._word_highlight_overlays:
                overlay.deleteLater()
            self._word_highlight_overlays.clear()
            
            if not self._current_page_words or not self._current_page_words.get("words"):
                return
            
            words = self._current_page_words["words"]
            page_pos = self._current_page_words["page_pos"]
            viewport_offset = self.verticalScrollBar().value()
            
            # Convert screen coordinates to PDF points
            start_x = (self._selection_start.x() - page_pos.x()) / self._zoom
            start_y = (self._selection_start.y() + viewport_offset - page_pos.y()) / self._zoom
            end_x = (current_pos.x() - page_pos.x()) / self._zoom
            end_y = (current_pos.y() + viewport_offset - page_pos.y()) / self._zoom
            
            # Selection bounds (normalize)
            sel_x0, sel_x1 = min(start_x, end_x), max(start_x, end_x)
            sel_y0, sel_y1 = min(start_y, end_y), max(start_y, end_y)
            
            # Find and highlight words in selection range
            from PyQt6.QtWidgets import QLabel
            from PyQt6.QtGui import QColor
            
            for word_data in words:
                x0, y0, x1, y1 = word_data[:4]
                word_cx = (x0 + x1) / 2
                word_cy = (y0 + y1) / 2
                
                if sel_x0 <= word_cx <= sel_x1 and sel_y0 <= word_cy <= sel_y1:
                    # Create highlight overlay for this word
                    # Convert PDF coords back to screen coords
                    screen_x = int(x0 * self._zoom + page_pos.x())
                    screen_y = int(y0 * self._zoom + page_pos.y() - viewport_offset)
                    screen_w = int((x1 - x0) * self._zoom)
                    screen_h = int((y1 - y0) * self._zoom)
                    
                    highlight = QLabel(self)
                    highlight.setStyleSheet("background-color: rgba(51, 153, 255, 0.4); border-radius: 2px;")
                    highlight.setGeometry(screen_x, screen_y, screen_w, screen_h)
                    highlight.show()
                    self._word_highlight_overlays.append(highlight)
                    
        except Exception as e:
            pass  # Silently fail to avoid spam during drag

    def _clear_word_highlights(self):
        """Clears all word highlight overlays."""
        for overlay in self._word_highlight_overlays:
            overlay.deleteLater()
        self._word_highlight_overlays.clear()




    def _process_selection(self, start, end):
        """Converte as coordenadas da tela para as coordenadas do PDF e extrai o texto."""
        # Achar em qual página o clique começou
        viewport_offset = self.verticalScrollBar().value()
        start_y_absolute = start.y() + viewport_offset
        
        for i, page in enumerate(self._pages):
            page_pos = page.pos()
            if page_pos.y() <= start_y_absolute <= page_pos.y() + page.height():
                # Encontrou a página
                # Converter coordenadas locais do widget para pontos do PDF (72 DPI)
                local_x = start.x() - page_pos.x()
                local_y = start_y_absolute - page_pos.y()
                
                # Coordenadas de fim relativas à mesma página
                local_x_end = end.x() - page_pos.x()
                local_y_end = end.y() + viewport_offset - page_pos.y()
                
                # Normalizar zoom para coordenadas PDF
                pdf_x0 = min(local_x, local_x_end) / self._zoom
                pdf_y0 = min(local_y, local_y_end) / self._zoom
                pdf_x1 = max(local_x, local_x_end) / self._zoom
                pdf_y1 = max(local_y, local_y_end) / self._zoom
                
                self.selectionChanged.emit((pdf_x0, pdf_y0, pdf_x1, pdf_y1))
                
                # Extrair texto real via PyMuPDF
                self._extract_and_copy_text(page.source_path, page.source_index, pdf_x0, pdf_y0, pdf_x1, pdf_y1)
                break

    def _extract_and_copy_text(self, source_path: str, page_index: int, x0: float, y0: float, x1: float, y1: float):
        """Extrai texto da área selecionada usando PyMuPDF e copia para o clipboard."""
        try:
            from src.infrastructure.adapters.pymupdf_adapter import PyMuPDFAdapter
            adapter = PyMuPDFAdapter()
            
            # Criar rect no formato PyMuPDF (x0, y0, x1, y1)
            rect = (x0, y0, x1, y1)
            
            # Open document and extract text
            text = adapter.get_text_in_rect(source_path, page_index, rect)
            
            if text and text.strip():
                # Copiar para o clipboard
                clipboard = QApplication.clipboard()
                clipboard.setText(text.strip())
                log_debug(f"Texto copiado para clipboard: {text[:50]}...")
                self.textExtracted.emit(text.strip())
            else:
                log_debug("Nenhum texto encontrado na área selecionada.")
        except Exception as e:
            log_exception(f"Erro ao extrair texto: {e}")

    def _cache_page_words_at_point(self, point: QPoint):
        """Cache words from the page at the given screen coordinate for flow selection."""
        try:
            viewport_offset = self.verticalScrollBar().value()
            y_absolute = point.y() + viewport_offset
            
            for i, page in enumerate(self._pages):
                page_pos = page.pos()
                if page_pos.y() <= y_absolute <= page_pos.y() + page.height():
                    # Found the page, cache its words
                    from src.infrastructure.adapters.pymupdf_adapter import PyMuPDFAdapter
                    import fitz
                    
                    with fitz.open(page.source_path) as doc:
                        fitz_page = doc[page.source_index]
                        # get_text("words") returns: (x0, y0, x1, y1, "word", block_n, line_n, word_n)
                        words = fitz_page.get_text("words")
                        self._current_page_words = {
                            "page_index": i,
                            "source_path": page.source_path,
                            "source_page": page.source_index,
                            "words": words,
                            "page_pos": page_pos
                        }
                    break
        except Exception as e:
            log_exception(f"Erro ao cachear palavras: {e}")
            self._current_page_words = {}

    def _process_flow_selection(self, end_pos: QPoint):
        """Processes flow selection by finding words between start and end positions."""
        try:
            log_debug(f"Flow selection: Starting with cache={bool(self._current_page_words)}")
            if not self._current_page_words or not self._current_page_words.get("words"):
                log_debug("Flow selection: No cached words, falling back to area selection")
                # Fallback to area selection if no words cached
                self._process_selection(self._selection_start, end_pos)
                return
            
            words = self._current_page_words["words"]
            page_pos = self._current_page_words["page_pos"]
            viewport_offset = self.verticalScrollBar().value()
            
            # Convert screen coordinates to PDF points
            start_x = (self._selection_start.x() - page_pos.x()) / self._zoom
            start_y = (self._selection_start.y() + viewport_offset - page_pos.y()) / self._zoom
            end_x = (end_pos.x() - page_pos.x()) / self._zoom
            end_y = (end_pos.y() + viewport_offset - page_pos.y()) / self._zoom
            
            log_debug(f"Flow selection: Area ({start_x:.0f},{start_y:.0f}) to ({end_x:.0f},{end_y:.0f}), {len(words)} words in page")
            
            # Find words in the selection range
            selected_words = []
            for word_data in words:
                x0, y0, x1, y1 = word_data[:4]
                word_text = word_data[4]
                
                # Check if word center is within selection range (simplified)
                word_cx = (x0 + x1) / 2
                word_cy = (y0 + y1) / 2
                
                # Selection bounds (normalize)
                sel_x0, sel_x1 = min(start_x, end_x), max(start_x, end_x)
                sel_y0, sel_y1 = min(start_y, end_y), max(start_y, end_y)
                
                if sel_x0 <= word_cx <= sel_x1 and sel_y0 <= word_cy <= sel_y1:
                    selected_words.append(word_text)
            
            if selected_words:
                text = " ".join(selected_words)
                clipboard = QApplication.clipboard()
                clipboard.setText(text)
                log_debug(f"Flow selection: {len(selected_words)} palavras copiadas para clipboard")
                self.textExtracted.emit(text)
            else:
                log_debug("Flow selection: Nenhuma palavra encontrada na área")
        except Exception as e:
            log_exception(f"Erro na seleção de fluxo: {e}")


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
