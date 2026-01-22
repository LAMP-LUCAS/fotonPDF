from pathlib import Path
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QFileDialog, QStatusBar, QToolBar, QLabel, QTabWidget)
from PyQt6.QtGui import QAction, QIcon, QDragEnterEvent, QDropEvent, QKeySequence
from PyQt6.QtCore import Qt, QSize

from src.interfaces.gui.widgets.viewer_widget import PDFViewerWidget
from src.interfaces.gui.widgets.thumbnail_panel import ThumbnailPanel
from src.interfaces.gui.widgets.search_panel import SearchPanel
from src.interfaces.gui.widgets.toc_panel import TOCPanel
from src.interfaces.gui.widgets.activity_bar import ActivityBar
from src.interfaces.gui.widgets.side_bar import SideBar
from PyQt6.QtWidgets import QSplitter

from src.infrastructure.adapters.pymupdf_adapter import PyMuPDFAdapter
from src.application.use_cases.export_image import ExportImageUseCase
from src.application.use_cases.export_svg import ExportSVGUseCase
from src.application.use_cases.export_markdown import ExportMarkdownUseCase
from src.application.use_cases.search_text import SearchTextUseCase
from src.application.use_cases.get_toc import GetTOCUseCase
from src.application.use_cases.detect_text_layer import DetectTextLayerUseCase
from src.application.use_cases.apply_ocr import ApplyOCRUseCase
from src.application.use_cases.ocr_area_extraction import OCRAreaExtractionUseCase

from src.infrastructure.services.logger import log_debug, log_exception
from src.interfaces.gui.styles import get_main_stylesheet
from src.infrastructure.services.resource_service import ResourceService
from src.infrastructure.services.settings_service import SettingsService
from src.application.use_cases.add_annotation import AddAnnotationUseCase
from src.application.use_cases.get_document_metadata import GetDocumentMetadataUseCase

def safe_callback(func):
    """Decorador para garantir resiliência em callbacks da UI."""
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            from src.infrastructure.services.logger import log_exception
            log_exception(f"UI Error Boundary [{func.__name__}]: {e}")
            if hasattr(self, 'statusBar'):
                self.statusBar().showMessage(f"⚠️ Erro em {func.__name__}: {e}")
    return wrapper

class MainWindow(QMainWindow):
    def __init__(self, initial_file=None):
        super().__init__()
        self.setWindowTitle("fotonPDF - Visualizador Profissional")
        self.setMinimumSize(1200, 800)
        
        # Central Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # --- NOVO LAYOUT VS CODE ---
        self.activity_bar = ActivityBar(self)
        self.side_bar = SideBar(self)
        
        # Splitter principal (Edição e Visualização)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        self.main_layout.addWidget(self.activity_bar)
        self.main_layout.addWidget(self.side_bar)
        self.main_layout.addWidget(self.splitter, stretch=1)

        # Use Cases & Adapter
        self._adapter = PyMuPDFAdapter()
        self._search_use_case = SearchTextUseCase(self._adapter)
        self._get_toc_use_case = GetTOCUseCase(self._adapter)
        self._get_metadata_use_case = GetDocumentMetadataUseCase(self._adapter)
        self._detect_ocr_use_case = DetectTextLayerUseCase(self._adapter)
        self._apply_ocr_use_case = ApplyOCRUseCase(self._adapter)
        self._ocr_area_use_case = OCRAreaExtractionUseCase(self._adapter)
        self._add_annot_use_case = AddAnnotationUseCase(self._adapter)

        # Components
        self.viewer = PDFViewerWidget()
        self.viewer2 = None # Para Split View
        self.thumbnails = ThumbnailPanel()
        self.toc_panel = TOCPanel(self._get_toc_use_case)
        self.search_panel = SearchPanel(self._search_use_case)

        # Adicionar painéis à SideBar
        self.side_bar.add_panel(self.thumbnails, "Explorer")
        self.side_bar.add_panel(self.search_panel, "Search")
        self.side_bar.add_panel(self.toc_panel, "Sumário")
        
        # Área de Visualização Principal (dentro do splitter)
        self.viewer_container = QWidget()
        self.vbox_viewer = QVBoxLayout(self.viewer_container)
        self.vbox_viewer.setContentsMargins(0, 0, 0, 0)
        self.vbox_viewer.setSpacing(0)
        
        # Banner OCR
        self._setup_ocr_banner()
        self.vbox_viewer.addWidget(self.ocr_banner)
        self.vbox_viewer.addWidget(self.viewer, stretch=1)
        
        self.splitter.addWidget(self.viewer_container)
        
        # Apply Visual Identity
        self.setStyleSheet(get_main_stylesheet())
        self._setup_window_icon()

        # UI Initialization
        self._setup_menus()
        self._setup_statusbar()
        self._setup_connections()

        # State
        self.current_file = None
        self.state_manager = None
        self.navigation_history = []
        self.history_index = -1
        self._is_navigating_history = False
        
        # Menu Contexto / Drag & Drop
        self.setAcceptDrops(True)
        self.thumbnails.setAcceptDrops(True)
        # Custom drop for thumbnails to handle APPEND
        self.thumbnails.dragEnterEvent = self._on_sidebar_drag_enter
        self.thumbnails.dropEvent = self._on_sidebar_drop

        # Placeholder Premium
        self._setup_placeholder()

        # Carregar configurações iniciais
        self._load_settings()

        if initial_file:
            self.open_file(Path(initial_file))
        elif (last := SettingsService.instance().get("last_file")):
             if Path(last).exists():
                 self.open_file(Path(last))

    def _load_settings(self):
        """Aplica preferências salvas do usuário."""
        settings = SettingsService.instance()
        
        # Modo de Leitura
        mode = settings.get("reading_mode", "default")
        self.viewer.set_reading_mode(mode)
        
        # Layout
        is_dual = settings.get_bool("dual_view", False)
        if is_dual:
            self.layout_action.setChecked(True)
            self.viewer.set_layout_mode("dual")
            
        # Zoom (Padrão 1.5 para conforto se for o primeiro boot)
        zoom = settings.get_float("zoom", 1.5)
        self.viewer.set_zoom(zoom)

    def closeEvent(self, event):
        """Salva o estado ao fechar."""
        settings = SettingsService.instance()
        settings.set("reading_mode", self.viewer._mode)
        settings.set("dual_view", self.viewer._layout_mode == "dual")
        settings.set("zoom", self.viewer._zoom)
        if self.current_file:
            settings.set("last_file", str(self.current_file))
        super().closeEvent(event)

    def _setup_window_icon(self):
        icon_path = ResourceService.get_logo_ico()
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

    def _setup_placeholder(self):
        placeholder = QWidget()
        vbox = QVBoxLayout(placeholder)
        vbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        logo_label = QLabel()
        icon_path = ResourceService.get_logo_svg()
        if icon_path.exists():
            pixmap = QIcon(str(icon_path)).pixmap(128, 128)
            logo_label.setPixmap(pixmap)
        
        text_label = QLabel("fotonPDF\nArraste um documento para iniciar sua jornada")
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_label.setStyleSheet("font-size: 24px; color: #94A3B8; font-weight: 300;")
        
        vbox.addWidget(logo_label)
        vbox.addWidget(text_label)
        
        self.viewer.setPlaceholder(placeholder)

    def _setup_ocr_banner(self):
        from PyQt6.QtWidgets import QFrame, QPushButton
        self.ocr_banner = QFrame()
        self.ocr_banner.setFixedHeight(40)
        self.ocr_banner.setStyleSheet("background-color: #34495e; border-bottom: 2px solid #2c3e50;")
        banner_layout = QHBoxLayout(self.ocr_banner)
        banner_layout.setContentsMargins(15, 0, 15, 0)
        
        self.banner_label = QLabel("Digitalizado detectado. Deseja aplicar OCR?")
        self.banner_label.setStyleSheet("color: #ecf0f1; font-weight: bold;")
        
        self.btn_apply_ocr = QPushButton("Aplicar OCR")
        self.btn_apply_ocr.setStyleSheet("background-color: #27ae60; color: white; border: none; padding: 5px 15px; border-radius: 3px;")
        self.btn_apply_ocr.clicked.connect(self._on_apply_ocr_clicked)
        
        banner_layout.addWidget(self.banner_label)
        banner_layout.addStretch()
        banner_layout.addWidget(self.btn_apply_ocr)
        self.ocr_banner.hide()

    def _setup_menus(self):
        menubar = self.menuBar()
        
        # --- MENU ARQUIVO ---
        file_menu = menubar.addMenu("&Arquivo")
        
        open_action = QAction("&Abrir...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._on_open_clicked)
        file_menu.addAction(open_action)
        
        self.save_action = QAction("&Salvar", self)
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.setEnabled(False)
        self.save_action.triggered.connect(self._on_save_clicked)
        file_menu.addAction(self.save_action)
        
        self.save_as_action = QAction("Salvar &Como...", self)
        self.save_as_action.setEnabled(False)
        self.save_as_action.triggered.connect(self._on_save_as_clicked)
        file_menu.addAction(self.save_as_action)
        
        file_menu.addSeparator()
        
        merge_action = QAction("&Unir PDFs...", self)
        merge_action.triggered.connect(self._on_merge_clicked)
        file_menu.addAction(merge_action)
        
        self.extract_action = QAction("&Extrair Páginas...", self)
        self.extract_action.setEnabled(False)
        self.extract_action.triggered.connect(self._on_extract_clicked)
        file_menu.addAction(self.extract_action)
        
        # Submenu Exportar
        export_menu = file_menu.addMenu("&Exportar")
        export_menu.addAction("Imagem High-DPI (PNG)").triggered.connect(lambda: self._on_export_image_clicked("png"))
        export_menu.addAction("SVG").triggered.connect(self._on_export_svg_clicked)
        export_menu.addAction("Markdown").triggered.connect(self._on_export_md_clicked)
        
        # --- MENU EDITAR ---
        edit_menu = menubar.addMenu("&Editar")
        
        self.rotate_left_action = QAction("Girar -90°", self)
        self.rotate_left_action.setEnabled(False)
        self.rotate_left_action.triggered.connect(lambda: self._on_rotate_clicked(-90))
        edit_menu.addAction(self.rotate_left_action)
        
        self.rotate_right_action = QAction("Girar +90°", self)
        self.rotate_right_action.setEnabled(False)
        self.rotate_right_action.triggered.connect(lambda: self._on_rotate_clicked(90))
        edit_menu.addAction(self.rotate_right_action)
        
        edit_menu.addSeparator()
        
        self.highlight_action = QAction("Modo Realçar (Highlight)", self)
        self.highlight_action.setCheckable(True)
        self.highlight_action.triggered.connect(self._on_highlight_toggled)
        edit_menu.addAction(self.highlight_action)
        
        # --- MENU VER ---
        view_menu = menubar.addMenu("&Ver")
        
        zoom_menu = view_menu.addMenu("&Zoom")
        zoom_menu.addAction("Aumentar").triggered.connect(self.viewer.zoom_in)
        zoom_menu.addAction("Diminuir").triggered.connect(self.viewer.zoom_out)
        zoom_menu.addAction("100%").triggered.connect(self.viewer.real_size)
        
        view_menu.addSeparator()
        
        self.back_action = QAction("⬅️ Voltar", self)
        self.back_action.setShortcut(QKeySequence.StandardKey.Back)
        self.back_action.setEnabled(False)
        self.back_action.triggered.connect(self._on_back_clicked)
        view_menu.addAction(self.back_action)
        
        self.forward_action = QAction("➡️ Avançar", self)
        self.forward_action.setShortcut(QKeySequence.StandardKey.Forward)
        self.forward_action.setEnabled(False)
        self.forward_action.triggered.connect(self._on_forward_clicked)
        view_menu.addAction(self.forward_action)
        
        view_menu.addSeparator()
        
        self.layout_action = QAction("&Lado a Lado (Páginas)", self)
        self.layout_action.setCheckable(True)
        self.layout_action.triggered.connect(self._on_layout_toggled)
        view_menu.addAction(self.layout_action)
        
        self.split_action = QAction("&Dividir Editor (Split)", self)
        self.split_action.setShortcut("Ctrl+\\")
        self.split_action.triggered.connect(self._on_split_clicked)
        view_menu.addAction(self.split_action)
        
        reading_menu = view_menu.addMenu("&Modo de Leitura")
        reading_menu.addAction("Padrão").triggered.connect(lambda: self.viewer.set_reading_mode("default"))
        reading_menu.addAction("Sépia").triggered.connect(lambda: self.viewer.set_reading_mode("sepia"))
        reading_menu.addAction("Noturno").triggered.connect(lambda: self.viewer.set_reading_mode("dark"))
        reading_menu.addAction("Madrugada").triggered.connect(lambda: self.viewer.set_reading_mode("night"))
        
        # --- MENU FERRAMENTAS ---
        tools_menu = menubar.addMenu("&Ferramentas")
        
        pan_action = QAction("✋ Mão (Pan)", self)
        pan_action.triggered.connect(lambda: self.viewer.set_tool_mode("pan"))
        tools_menu.addAction(pan_action)
        
        select_action = QAction("🖱️ Ponteiro (Seleção)", self)
        select_action.triggered.connect(lambda: self.viewer.set_tool_mode("selection"))
        tools_menu.addAction(select_action)
        
        tools_menu.addSeparator()
        
        self.ocr_area_action = QAction("🧠 OCR p/ Área", self)
        self.ocr_area_action.setCheckable(True)
        self.ocr_area_action.setEnabled(False)
        self.ocr_area_action.triggered.connect(self._on_ocr_area_toggled)
        tools_menu.addAction(self.ocr_area_action)

    def _setup_statusbar(self):
        from PyQt6.QtWidgets import QPushButton, QHBoxLayout, QFrame
        
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Pronto")
        
        # Container para botões de toggle (Layout) na direita
        self.status_controls = QWidget()
        layout = QHBoxLayout(self.status_controls)
        layout.setContentsMargins(0, 0, 5, 0)
        layout.setSpacing(2)
        
        # Botão Toggle SideBar
        self.btn_toggle_sidebar = QPushButton("▥")
        self.btn_toggle_sidebar.setToolTip("Alternar Side Bar")
        self.btn_toggle_sidebar.setFixedSize(24, 20)
        self.btn_toggle_sidebar.setStyleSheet("background: transparent; border: none; color: #858585;")
        self.btn_toggle_sidebar.clicked.connect(self.side_bar.toggle_collapse)
        
        # Botão Toggle ActivityBar
        self.btn_toggle_activity = QPushButton("┇")
        self.btn_toggle_activity.setToolTip("Alternar Activity Bar")
        self.btn_toggle_activity.setFixedSize(24, 20)
        self.btn_toggle_activity.setStyleSheet("background: transparent; border: none; color: #858585;")
        self.btn_toggle_activity.clicked.connect(self._on_toggle_activity_bar)
        
        layout.addWidget(self.btn_toggle_sidebar)
        layout.addWidget(self.btn_toggle_activity)
        
        self.statusBar().addPermanentWidget(self.status_controls)

    def _on_toggle_activity_bar(self):
        """Alterna a visibilidade da barra de atividades."""
        visible = self.activity_bar.isVisible()
        self.activity_bar.setVisible(not visible)

    def _setup_connections(self):
        self.thumbnails.pageSelected.connect(self.viewer.scroll_to_page)
        self.thumbnails.orderChanged.connect(self._on_pages_reordered)
        
        self.viewer.pageChanged.connect(self._on_page_changed)
        self.search_panel.result_clicked.connect(self.viewer.scroll_to_page)
        self.search_panel.results_found.connect(self._on_search_results_found)
        self.toc_panel.bookmark_clicked.connect(self.viewer.scroll_to_page)
        
        # Conexão da Activity Bar
        self.activity_bar.clicked.connect(self._on_activity_clicked)
        
        # Conexão da Floating Nav Bar
        self.viewer.nav_bar.toggleSplit.connect(self._on_split_clicked)
        
        # Atalhos
        self.search_shortcut = QAction("Search", self)
        self.search_shortcut.setShortcut(QKeySequence("Ctrl+F"))
        self.search_shortcut.triggered.connect(self._focus_search)
        self.addAction(self.search_shortcut)

        self.viewer.areaSelected.connect(self._on_area_selected)

    def _on_activity_clicked(self, idx):
        titles = {0: "EXPLORER", 1: "SEARCH", 2: "SUMÁRIO", 3: "ANNOTATIONS"}
        
        if idx == 99:
             return
             
        # Se clicar no ícone que já está ativo, colapsa/expande a sidebar (estilo VS Code)
        if self.side_bar.stack.currentIndex() == idx and not self.side_bar._is_collapsed:
            self.side_bar.toggle_collapse()
        else:
            self.side_bar.show_panel(idx, titles.get(idx, ""))

    def _on_search_results_found(self, results):
        """Atualiza os marcadores na barra de rolagem."""
        if not self.state_manager: return
        
        page_count = self.state_manager.get_page_count()
        if page_count == 0: return
        
        # Calcular posições relativas (0.0 a 1.0)
        positions = [res.page_index / page_count for res in results]
        
        # Definir marcadores na scrollbar do viewer
        self.viewer.verticalScrollBar().set_markers(positions)

    def open_file(self, file_path: Path):
        try:
            # Segurança: Sanitize Path
            file_path = Path(file_path).resolve()
            if not file_path.exists():
                raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

            self.current_file = file_path
            from src.interfaces.gui.state.pdf_state import PDFStateManager
            self.state_manager = PDFStateManager()
            self.state_manager.load_base_document(str(file_path))
            
            # Obter metadados via Caso de Uso (Arquitetura Hexagonal)
            metadata = self._get_metadata_use_case.execute(file_path)
            
            self.viewer.load_document(file_path, metadata)
            self.thumbnails.load_thumbnails(str(file_path), metadata["page_count"])
            SettingsService.instance().set("last_file", str(file_path))
            
            # Inicializar painéis da Sprint 6
            self.toc_panel.set_pdf(file_path)
            self.search_panel.set_pdf(file_path)
            
            # Detecção de OCR (Sprint 7)
            self._check_ocr_needed(file_path)
            
            self.setWindowTitle(f"fotonPDF - {file_path.name}")
            self.statusBar().showMessage(f"Arquivo carregado: {file_path.name}")
            self._enable_actions(True)
            
            # Reset History
            self.navigation_history = [0]
            self.history_index = 0
            self._update_history_buttons()
        except Exception as e:
            log_exception(f"MainWindow: Erro ao abrir: {e}")
            self.statusBar().showMessage(f"Erro: {e}")

    @safe_callback
    def _on_page_changed(self, index: int):
        """Sincroniza a seleção da sidebar com a página atual do viewer."""
        self.thumbnails.set_selected_page(index)
        
        if self._is_navigating_history:
            return
            
        # Só adiciona se for uma página diferente da atual no histórico
        if not self.navigation_history or self.navigation_history[self.history_index] != index:
            # Ao navegar para uma nova página, corta o futuro se houver
            self.navigation_history = self.navigation_history[:self.history_index + 1]
            self.navigation_history.append(index)
            self.history_index += 1
            
            # Limitar tamanho do histórico
            if len(self.navigation_history) > 50:
                self.navigation_history.pop(0)
                self.history_index -= 1
                
            self._update_history_buttons()

    def _enable_actions(self, enabled: bool):
        self.save_action.setEnabled(enabled)
        self.save_as_action.setEnabled(enabled)
        self.rotate_left_action.setEnabled(enabled)
        self.rotate_right_action.setEnabled(enabled)
        self.extract_action.setEnabled(enabled)
        self.back_action.setEnabled(enabled)
        self.forward_action.setEnabled(enabled)
        # Habilitar OCR se o motor existir
        self.ocr_area_action.setEnabled(enabled and self._adapter.is_engine_available())

    @safe_callback
    def _on_save_clicked(self):
        """Sobrescreve o arquivo atual."""
        if not self.state_manager or not self.current_file: return
        try:
            self.state_manager.save(str(self.current_file))
            self.statusBar().showMessage(f"Arquivo salvo: {self.current_file.name}")
        except Exception as e:
            self.statusBar().showMessage(f"Erro ao salvar: {e}")

    @safe_callback
    def _on_save_as_clicked(self):
        """Salva o estado atual em um novo local."""
        if not self.state_manager: return
        file_path, _ = QFileDialog.getSaveFileName(self, "Salvar PDF Como", "", "Arquivos PDF (*.pdf)")
        if file_path:
            self.state_manager.save(file_path)
            self.statusBar().showMessage(f"Salvo como: {Path(file_path).name}")

    @safe_callback
    def _on_extract_clicked(self):
        """Salva as páginas selecionadas em um novo arquivo."""
        if not self.state_manager: return
        selected_rows = self.thumbnails.get_selected_rows()
        if not selected_rows:
            self.statusBar().showMessage("Selecione páginas na barra lateral para extrair.")
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Extrair Páginas", "extracao.pdf", "Arquivos PDF (*.pdf)")
        if not file_path: return

        try:
            # Salva o subconjunto baseado na ordem visual atual
            self.state_manager.save(file_path, indices=selected_rows)
            self.statusBar().showMessage(f"Extraídas {len(selected_rows)} páginas para {Path(file_path).name}")
        except Exception as e:
            self.statusBar().showMessage(f"Erro ao extrair: {e}")

    @safe_callback
    def _on_export_image_clicked(self, fmt: str):
        """Exporta a página atual como imagem (High-DPI)."""
        if not self.state_manager: return
        idx = self.viewer.get_current_page_index()
        page_state = self.state_manager.get_page(idx)
        if not page_state: return

        file_path, _ = QFileDialog.getSaveFileName(self, "Exportar Página", f"pagina_{idx+1}.{fmt}", f"Imagens (*.{fmt})")
        if not file_path: return

        try:
            # Usar o Use Case para exportação (Desacoplamento)
            adapter = PyMuPDFAdapter()
            use_case = ExportImageUseCase(adapter)
            
            source_path = Path(page_state.source_doc.name)
            
            # exec retorna uma lista de caminhos
            output_paths = use_case.execute(
                source_path, 
                page_state.source_page_index, 
                Path(file_path).parent, # Salvar no diretório pai 
                fmt=fmt, 
                dpi=300
            )
            
            self.statusBar().showMessage(f"Página {idx+1} exportada para {output_paths[0].name}.")
        except Exception as e:
            self.statusBar().showMessage(f"Erro ao exportar imagem: {e}")
            log_exception(f"Export: {e}")

    @safe_callback
    def _on_export_svg_clicked(self):
        """Exporta a página atual como SVG."""
        if not self.state_manager: return
        idx = self.viewer.get_current_page_index()
        page_state = self.state_manager.get_page(idx)
        if not page_state: return

        file_path, _ = QFileDialog.getSaveFileName(self, "Exportar SVG", f"pagina_{idx+1}.svg", "SVG (*.svg)")
        if not file_path: return

        try:
            adapter = PyMuPDFAdapter()
            use_case = ExportSVGUseCase(adapter)
            
            source_path = Path(page_state.source_doc.name)
            output_paths = use_case.execute(source_path, page_state.source_page_index, Path(file_path).parent)
            
            self.statusBar().showMessage(f"Página {idx+1} exportada para {output_paths[0].name}.")
        except Exception as e:
            self.statusBar().showMessage(f"Erro ao exportar SVG: {e}")

    @safe_callback
    def _on_export_md_clicked(self):
        """Exporta o conteúdo do documento como Markdown."""
        if not self.state_manager: return
        file_path, _ = QFileDialog.getSaveFileName(self, "Exportar Markdown", "documento.md", "Markdown (*.md)")
        if not file_path: return

        try:
            adapter = PyMuPDFAdapter()
            use_case = ExportMarkdownUseCase(adapter)
            
            # No caso da GUI, se houver um arquivo aberto, usamos ele.
            # Nota: O export-md na CLI exporta o arquivo todo. 
            # Na GUI, se houver um arquivo base, exportamos ele.
            if self.current_file:
                use_case.execute(self.current_file, Path(file_path))
                self.statusBar().showMessage("Documento exportado como Markdown.")
            else:
                self.statusBar().showMessage("Nenhum arquivo base para exportar.")
        except Exception as e:
            self.statusBar().showMessage(f"Erro ao exportar Markdown: {e}")

    def _on_open_clicked(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Abrir PDF", "", "Arquivos PDF (*.pdf)")
        if file_path:
            self.open_file(Path(file_path))

    def _on_merge_clicked(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Unir PDFs", "", "Arquivos PDF (*.pdf)")
        for f in files:
            self._append_pdf(Path(f))

    @safe_callback
    def _append_pdf(self, path: Path):
        """Implementação do Merge 2.0 (Incremental)."""
        try:
            # Segurança: Sanitize Path
            path = Path(path).resolve()
            if not path.exists():
                return

            if not self.state_manager:
                self.open_file(path)
                return

            metadata = self._get_metadata_use_case.execute(path)
            self.state_manager.append_document(str(path))
            # Atualizar viewer e sidebar instantaneamente
            self.viewer.add_pages(path, metadata)
            self.thumbnails.append_thumbnails(str(path), metadata["page_count"])
            self.statusBar().showMessage(f"Adicionado: {path.name}")
        except Exception as e:
            log_exception(f"MainWindow: Erro ao anexar: {e}")
            self.statusBar().showMessage(f"Erro ao anexar arquivo: {e}")

    @safe_callback
    def _on_rotate_clicked(self, degrees: int):
        # Segurança: Sanitize Path
        if self.current_file:
            self.current_file = self.current_file.resolve()
        # Agora usamos as linhas VISUAIS
        selected_rows = self.thumbnails.get_selected_rows()
        if not selected_rows:
            self.statusBar().showMessage("Selecione páginas na barra lateral para girar.")
            return

        for idx in selected_rows:
            self.state_manager.rotate_page(idx, degrees)
            page_state = self.state_manager.get_page(idx)
            # Atualizar o widget na posição 'idx'
            self.viewer.refresh_page(idx, rotation=page_state.absolute_rotation)
        
        self.statusBar().showMessage(f"Giro de {degrees}° aplicado.")

    def _on_pages_reordered(self, new_order: list[int]):
        """Sincroniza viewer e state com a nova ordem da sidebar."""
        if self.state_manager:
            self.state_manager.reorder_pages(new_order)
            self.viewer.reorder_pages(new_order)
            # Reset history after reorder to avoid confusion
            self.navigation_history = [self.viewer.get_current_page_index()]
            self.history_index = 0
            self._update_history_buttons()

    def _focus_search(self):
        """Atalho Ctrl+F: foca no painel de busca."""
        self.activity_bar.set_active(1)
        self._on_activity_clicked(1)
        self.search_panel.search_input.setFocus()

    @safe_callback
    def _on_split_clicked(self):
        """Ativa/Desativa o modo Split Editor para documentos distintos."""
        if self.viewer2 is None:
            # Ativar Split
            file_path, _ = QFileDialog.getOpenFileName(self, "Abrir Segundo PDF (Split)", "", "Arquivos PDF (*.pdf)")
            if not file_path: return
            
            self.viewer2 = PDFViewerWidget()
            # Precisamos de um novo State Manager se quisermos edições independentes,
            # mas para visualização clean, vamos focar no loading.
            metadata = self._get_metadata_use_case.execute(Path(file_path))
            self.viewer2.load_document(Path(file_path), metadata)
            
            self.splitter.addWidget(self.viewer2)
            self.statusBar().showMessage(f"Split: {Path(file_path).name} aberto à direita.")
        else:
            # Desativar Split
            self.viewer2.deleteLater()
            self.viewer2 = None
            self.statusBar().showMessage("Split Editor fechado.")

        # Só adiciona se for uma página diferente da atual no histórico
        if not self.navigation_history or self.navigation_history[self.history_index] != index:
            # Ao navegar para uma nova página, corta o futuro se houver
            self.navigation_history = self.navigation_history[:self.history_index + 1]
            self.navigation_history.append(index)
            self.history_index += 1
            
            # Limitar tamanho do histórico
            if len(self.navigation_history) > 50:
                self.navigation_history.pop(0)
                self.history_index -= 1
                
            self._update_history_buttons()

    def _on_back_clicked(self):
        if self.history_index > 0:
            self._is_navigating_history = True
            self.history_index -= 1
            page = self.navigation_history[self.history_index]
            self.viewer.scroll_to_page(page)
            self._is_navigating_history = False
            self._update_history_buttons()

    def _on_forward_clicked(self):
        if self.history_index < len(self.navigation_history) - 1:
            self._is_navigating_history = True
            self.history_index += 1
            page = self.navigation_history[self.history_index]
            self.viewer.scroll_to_page(page)
            self._is_navigating_history = False
            self._update_history_buttons()

    def _update_history_buttons(self):
        self.back_action.setEnabled(self.history_index > 0)
        self.forward_action.setEnabled(self.history_index < len(self.navigation_history) - 1)

    def _check_ocr_needed(self, file_path: Path):
        """Verifica se o PDF precisa de OCR e se o motor está disponível."""
        try:
            is_searchable = self._detect_ocr_use_case.execute(file_path)
            has_engine = self._adapter.is_engine_available()
            
            if not is_searchable and has_engine:
                self.ocr_banner.show()
                log_debug("OCR: Documento não-pesquisável detectado. Sugestão exibida.")
            else:
                self.ocr_banner.hide()
        except Exception as e:
            log_exception(f"OCR Detection: {e}")

    @safe_callback
    def _on_apply_ocr_clicked(self):
        """Executa o OCR no documento inteiro."""
        if not self.current_file: return
        
        self.btn_apply_ocr.setEnabled(False)
        self.btn_apply_ocr.setText("Processando...")
        self.statusBar().showMessage("Executando OCR no documento... Isso pode levar alguns minutos.")
        
        # Usar QTimer para não travar a UI (mesmo que seja blocking no adapter por enquanto, 
        # o ideal seria QThread, mas para manter o padrão hexagonal simples...)
        QTimer.singleShot(100, self._process_ocr)

    def _process_ocr(self):
        try:
            new_path = self._apply_ocr_use_case.execute(self.current_file)
            self.ocr_banner.hide()
            self.statusBar().showMessage(f"OCR Concluído! Novo arquivo: {new_path.name}")
            
            # Pergunta se deseja abrir o novo arquivo
            from PyQt6.QtWidgets import QMessageBox
            reply = QMessageBox.question(self, "OCR Concluído", 
                                       f"O documento foi processado e salvo como:\n{new_path.name}\n\nDeseja abrir a versão pesquisável agora?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                self.open_file(new_path)
        except Exception as e:
            log_exception(f"OCR Process: {e}")
            self.statusBar().showMessage(f"Erro no OCR: {str(e)}")
        finally:
            self.btn_apply_ocr.setEnabled(True)
            self.btn_apply_ocr.setText("Aplicar OCR")

    def _on_ocr_area_toggled(self, checked: bool):
        self.viewer.set_selection_mode(checked)
        if checked:
            self.statusBar().showMessage("Modo de Seleção OCR Ativo: Desenhe um retângulo sobre o texto na imagem.")
        else:
            self.statusBar().showMessage("Modo de Seleção OCR Desativado.")

    def _on_layout_toggled(self, checked: bool):
        """Alterna entre visão única e visão dupla."""
        mode = "dual" if checked else "single"
        self.viewer.set_layout_mode(mode)
        self.statusBar().showMessage(f"Modo de Visualização: {'Lado a Lado' if checked else 'Página Única'}")

    def _on_highlight_toggled(self, checked: bool):
        """Ativa/Desativa o modo de seleção para anotação."""
        if checked:
            # Desativar outros modos de área
            self.ocr_area_action.setChecked(False)
            self.viewer.set_area_selection_mode(True)
            self.statusBar().showMessage("Modo Realce Ativado: Desenhe um retângulo sobre o texto.")
        else:
            self.viewer.set_area_selection_mode(False)
            self.statusBar().showMessage("Modo Realce Desativado.")

    def _on_area_selected(self, page_index, rect):
        """Chamado quando o usuário desenha uma área no viewer."""
        if not self.current_file: return
        
        # Se estivermos no modo OCR
        if self.ocr_area_action.isChecked():
            self._handle_ocr_area(page_index, rect)
        # Se estivermos no modo Realce
        elif self.highlight_action.isChecked():
            self._handle_highlight_area(page_index, rect)

    def _handle_ocr_area(self, page_index, rect):
        try:
            self.statusBar().showMessage("Extraindo texto da área selecionada...")
            text = self._ocr_area_use_case.execute(self.current_file, page_index, rect)
            
            if text:
                from PyQt6.QtWidgets import QApplication
                QApplication.clipboard().setText(text)
                self.statusBar().showMessage(f"Texto extraído: '{text[:30]}...' (Copiado para área de transferência)")
            else:
                self.statusBar().showMessage("Nenhum texto detectado na área selecionada.")
                
            self.ocr_area_action.setChecked(False)
            self.viewer.set_area_selection_mode(False)
            
        except Exception as e:
            log_exception(f"OCR Area Selection: {e}")
            self.statusBar().showMessage(f"Erro na extração: {e}")

    def _handle_highlight_area(self, page_index, rect):
        try:
            self.statusBar().showMessage("Aplicando realce...")
            new_path = self._add_annot_use_case.execute(
                self.current_file, 
                page_index, 
                rect, 
                type="highlight", 
                color=(1, 1, 0) # Amarelo padrão
            )
            
            # Recarregar o arquivo para mostrar a anotação (Fóton 2.0 é imutável no estado, então abrimos o novo)
            self.open_file(new_path)
            self.statusBar().showMessage("Realce aplicado com sucesso!")
            
            self.highlight_action.setChecked(False)
            self.viewer.set_area_selection_mode(False)
            
        except Exception as e:
            log_exception(f"Highlight: {e}")
            self.statusBar().showMessage(f"Erro ao realçar: {e}")

    # --- Re-implementação de Drag & Drop para Sidebar (Merge) ---
    def _on_sidebar_drag_enter(self, event):
        if event.mimeData().hasUrls(): event.accept()
        else: event.ignore()

    def _on_sidebar_drop(self, event):
        urls = event.mimeData().urls()
        for url in urls:
            path = Path(url.toLocalFile())
            if path.suffix.lower() == ".pdf":
                self._append_pdf(path)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls(): event.accept()
        else: event.ignore()

    def dropEvent(self, event: QDropEvent):
        # Drop no corpo principal -> ABRIR NOVO (Reset)
        urls = event.mimeData().urls()
        if urls:
            path = Path(urls[0].toLocalFile())
            if path.suffix.lower() == ".pdf":
                self.open_file(path)
