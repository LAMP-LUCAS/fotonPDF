from pathlib import Path
import time
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QFileDialog, QStatusBar, QToolBar, QLabel, QTabWidget, QTextEdit, QStackedWidget)
from PyQt6.QtGui import QAction, QIcon, QDragEnterEvent, QDropEvent, QKeySequence
from PyQt6.QtCore import Qt, QSize, QTimer
import socket

from src.interfaces.gui.widgets.viewer_widget import PDFViewerWidget
from src.interfaces.gui.widgets.thumbnail_panel import ThumbnailPanel
from src.interfaces.gui.widgets.search_panel import SearchPanel
from src.interfaces.gui.widgets.toc_panel import TOCPanel
from src.interfaces.gui.widgets.activity_bar import ActivityBar
from src.interfaces.gui.widgets.side_bar import SideBar
from src.interfaces.gui.widgets.tab_container import TabContainer
from src.interfaces.gui.widgets.bottom_panel import BottomPanel
from src.interfaces.gui.widgets.editor_group import EditorGroup
from src.interfaces.gui.widgets.command_palette import CommandPalette
from src.interfaces.gui.widgets.infinite_canvas import InfiniteCanvasView
from src.interfaces.gui.widgets.light_table_view import LightTableView
from PyQt6.QtWidgets import QSplitter
from PyQt6.QtCore import Qt, QSize, QTimer

from src.infrastructure.adapters.pymupdf_adapter import PyMuPDFAdapter
from src.application.use_cases.export_image import ExportImageUseCase
from src.application.use_cases.export_svg import ExportSVGUseCase
from src.application.use_cases.export_markdown import ExportMarkdownUseCase
from src.application.use_cases.search_text import SearchTextUseCase
from src.application.use_cases.get_toc import GetTOCUseCase
from src.application.use_cases.detect_text_layer import DetectTextLayerUseCase
from src.application.use_cases.apply_ocr import ApplyOCRUseCase
from src.application.use_cases.ocr_area_extraction import OCRAreaExtractionUseCase

from src.infrastructure.services.logger import log_debug, log_exception, log_error
from src.interfaces.gui.styles import get_main_stylesheet
from src.infrastructure.services.resource_service import ResourceService
from src.infrastructure.services.settings_service import SettingsService
from src.application.use_cases.add_annotation import AddAnnotationUseCase
from src.application.use_cases.get_document_metadata import GetDocumentMetadataUseCase

from src.interfaces.gui.utils.ui_error_boundary import safe_ui_callback
from src.interfaces.gui.state.pdf_state import PDFStateManager
from src.infrastructure.services.telemetry_service import TelemetryService
from src.interfaces.gui.utils.document_loader import AsyncDocumentLoader
from src.infrastructure.services.startup_logger import StartupLogger
from src.interfaces.gui.controllers.workspace_controller import WorkspaceController

class MainWindow(QMainWindow):
    @property
    def viewer(self):
        """Retorna o visualizador principal da aba ativa."""
        if hasattr(self, 'tabs'):
            editor = self.tabs.current_editor()
            return editor.get_viewer() if editor else None
        return None

    def _on_layer_toggle(self, file_path, layer_id, visible):
        """Callback from Inspector to toggle PDF layers (OCG)."""
        if str(file_path) != str(self.current_file): return
        
        log_debug(f"MainWindow: Layer Toggle -> ID={layer_id} Visible={visible}")
        if self.viewer:
             self.viewer.update_render_config({layer_id: visible})

    @property
    def current_editor_group(self):
        """Retorna o EditorGroup ativo."""
        if hasattr(self, 'tabs'):
            return self.tabs.current_editor()
        return None

    @property
    def state_manager(self):
        """Retorna o StateManager (Virtual State) da aba ativa."""
        group = self.current_editor_group
        if group and hasattr(group, 'state_manager'):
            return group.state_manager
        # Fallback durante inicialização ou se não houver abas
        if not hasattr(self, '_fallback_state_manager'):
            from src.interfaces.gui.state.pdf_state import PDFStateManager
            self._fallback_state_manager = PDFStateManager()
        return self._fallback_state_manager

    def __init__(self, initial_file=None, settings_connector=None):
        super().__init__()
        self._settings_connector = settings_connector
        self.setWindowTitle("fotonPDF - Visualizador Profissional")
        self.setMinimumSize(1200, 800)
        
        # Helper for startup logging (Delegated to StartupLogger)
        StartupLogger.clear()
        
        # Stage 1: Adapter & Infrastructure
        try:
            self._adapter = PyMuPDFAdapter()
            # Injeção de dependência no motor de renderização (Arquitetura Hexagonal)
            from src.interfaces.gui.state.render_engine import RenderEngine
            RenderEngine.instance(adapter=self._adapter)
            
            from src.infrastructure.repositories.sqlite_stage_repository import StageStateRepository
            self.persistence = StageStateRepository(Path("stage_state.db"))
            StartupLogger.log("Stage1_Infrastructure")
        except Exception as e:
            StartupLogger.log("Stage1_Infrastructure", e)
            log_exception(f"Stage1 failed: {e}")
            self._adapter = None
            self.persistence = None
        
        # Stage 2: Use Cases
        try:
            if self._adapter:
                self._search_use_case = SearchTextUseCase(self._adapter)
                self._get_toc_use_case = GetTOCUseCase(self._adapter)
                self._get_metadata_use_case = GetDocumentMetadataUseCase(self._adapter)
                self._detect_ocr_use_case = DetectTextLayerUseCase(self._adapter)
                self._apply_ocr_use_case = ApplyOCRUseCase(self._adapter)
                self._ocr_area_use_case = OCRAreaExtractionUseCase(self._adapter)
                self._add_annot_use_case = AddAnnotationUseCase(self._adapter)
            else:
                self._search_use_case = self._get_toc_use_case = None
                self._get_metadata_use_case = self._detect_ocr_use_case = None
                self._apply_ocr_use_case = self._ocr_area_use_case = None
                self._add_annot_use_case = None
            StartupLogger.log("Stage2_UseCases")
        except Exception as e:
            StartupLogger.log("Stage2_UseCases", e)
            log_exception(f"Stage2 failed: {e}")
        
        # Stage 3: Orchestrator (Lazy AI)
        try:
            from src.application.services.command_orchestrator import CommandOrchestrator
            self.orchestrator = CommandOrchestrator(self._adapter) if self._adapter else None
            StartupLogger.log("Stage3_Orchestrator")
        except Exception as e:
            StartupLogger.log("Stage3_Orchestrator", e)
            log_exception(f"Orchestrator init failed: {e}")
            self.orchestrator = None

        # Stage 4: UI State
        try:
            self.current_file = None
            # Removida instância fixa: agora é per-aba via propriedade
            self.workspace_controller = WorkspaceController(self) # Novo Controller
            self.navigation_history = []
            self.history_index = -1
            self._is_navigating_history = False
            StartupLogger.log("Stage4_UIState")
        except Exception as e:
            StartupLogger.log("Stage4_UIState", e)
            log_exception(f"UI State init failed: {e}")

        # Stage 5: UI Setup
        try:
            self._setup_ui_v4()
            StartupLogger.log("Stage5_SetupUI")
        except Exception as e:
            StartupLogger.log("Stage5_SetupUI", e)
            log_exception(f"UI Setup failed: {e}")
            # Create minimal fallback UI
            from PyQt6.QtWidgets import QLabel
            central = QLabel("Erro na criação da interface. Verifique o log.")
            central.setStyleSheet("color: red; font-size: 16px; padding: 20px;")
            self.setCentralWidget(central)
            return  # Skip remaining setup

        # Stage 6: Menus & Status
        try:
            self._setup_menus()
            self._setup_statusbar()
            StartupLogger.log("Stage6_MenusStatusbar")
        except Exception as e:
            StartupLogger.log("Stage6_MenusStatusbar", e)
            log_exception(f"Menus/Statusbar failed: {e}")
        
        # Stage 7: Connections
        try:
            self._setup_connections_v4()
            StartupLogger.log("Stage7_Connections")
        except Exception as e:
            StartupLogger.log("Stage7_Connections", e)
            log_exception(f"Connections failed: {e}")
            if hasattr(self, "bottom_panel"):
                self.bottom_panel.add_log(f"⚠️ Erro de Conexões: {e}", color="orange")
        
        # Stage 8: Styling
        try:
            self.setStyleSheet(get_main_stylesheet())
            self._setup_window_icon()
            StartupLogger.log("Stage8_Styling")
        except Exception as e:
            StartupLogger.log("Stage8_Styling", e)
            log_exception(f"Styling failed: {e}")

        # Stage 9: Final Setup
        try:
            self.setAcceptDrops(True)
            self._load_settings()
            
            # Garantir que a SideBar esquerda inicie colapsada (conforme pedido do usuário)
            # Usamos singleShot para evitar conflito com a restauração de geometria/estado no startup
            if hasattr(self, 'side_bar') and self.side_bar:
                QTimer.singleShot(500, self.side_bar.collapse)
            
            StartupLogger.log("Stage9_FinalSetup")
        except Exception as e:
            StartupLogger.log("Stage9_FinalSetup", e)
            log_exception(f"Final setup failed: {e}")

        # Open initial file if provided
        if initial_file:
            QTimer.singleShot(100, lambda: self.open_file(Path(initial_file)))
        
        # Stage 10: Heartbeat (Dev Mode)
        try:
            self._heartbeat_timer = QTimer(self)
            self._heartbeat_timer.timeout.connect(self._send_heartbeat)
            self._heartbeat_timer.start(1000)
            self._hb_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except:
            pass
            
        StartupLogger.log("__init__COMPLETE")

    def _send_heartbeat(self):
        """Monitor de saúde da GUI: envia ping para o hot-reload."""
        try:
            self._hb_sock.sendto(b"1", ("127.0.0.1", 9999))
        except:
            pass

    def _setup_ui_v4(self):
        """Organização modular orientada a plugins e alta performance."""
        
        StartupLogger.log("START_UI_V4")
        
        # Import widgets with logging
        try:
            from src.interfaces.gui.widgets.top_bar import TopBarWidget
            StartupLogger.log("import TopBarWidget")
        except Exception as e:
            StartupLogger.log("import TopBarWidget", e)
            TopBarWidget = None
            
        try:
            from src.interfaces.gui.widgets.inspector_panel import InspectorPanel
            StartupLogger.log("import InspectorPanel")
        except Exception as e:
            StartupLogger.log("import InspectorPanel", e)
            InspectorPanel = None
        
        # Central Widget & Main Layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.outer_layout = QVBoxLayout(self.central_widget)
        self.outer_layout.setContentsMargins(0, 0, 0, 0)
        self.outer_layout.setSpacing(0)
        StartupLogger.log("central_widget")
        
        # 1. Top Bar
        try:
            self.top_bar = TopBarWidget(self) if TopBarWidget else QWidget()
            self.top_bar.searchTriggered.connect(self._on_search_triggered)
            if hasattr(self.top_bar, 'searchChanged'):
                self.top_bar.searchChanged.connect(self._on_search_changed)
            self.top_bar.toggleRequested.connect(self._on_layout_toggle_requested)
            self.top_bar.viewModeChanged.connect(self._switch_view_mode_v4)
            StartupLogger.log("TopBar")
        except Exception as e:
            StartupLogger.log("TopBar", e)
            self.top_bar = QWidget()
        
        # 2. Body Layout
        self.body_container = QWidget()
        self.body_layout = QHBoxLayout(self.body_container)
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(0)
        StartupLogger.log("body_container")
        
        try:
            should_load_sidebar = SettingsService.instance().get_bool("startup_load_sidebar", True)
            
            if should_load_sidebar:
                self.activity_bar = ActivityBar(self)
                StartupLogger.log("ActivityBar")
            else:
                self.activity_bar = QWidget()
                self.activity_bar.setVisible(False)
                StartupLogger.log("ActivityBar (Disabled)")
        except Exception as e:
            StartupLogger.log("ActivityBar", e)
            self.activity_bar = QWidget()
            
        try:
            should_load_sidebar = SettingsService.instance().get_bool("startup_load_sidebar", True)
            
            if should_load_sidebar:
                self.side_bar = SideBar(self, initial_width=250, settings_prefix="sidebar_left")
                StartupLogger.log("SideBar_left")
            else:
                self.side_bar = QWidget()
                self.side_bar.setVisible(False)
                StartupLogger.log("SideBar_left (Disabled)")
        except Exception as e:
            StartupLogger.log("SideBar_left", e)
            self.side_bar = QWidget()
            
        try:
            should_load_sidebar = SettingsService.instance().get_bool("startup_load_sidebar", True)

            if should_load_sidebar:
                self.side_bar_right = SideBar(self, initial_width=300, settings_prefix="sidebar_right")
                self.side_bar_right.set_title("AEC INSPECTOR")
                StartupLogger.log("SideBar_right")
            else:
                self.side_bar_right = QWidget()
                self.side_bar_right.setVisible(False)
                StartupLogger.log("SideBar_right (Disabled)")
        except Exception as e:
            StartupLogger.log("SideBar_right", e)
            self.side_bar_right = QWidget()
        
        self.horizontal_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.central_splitter = QSplitter(Qt.Orientation.Vertical)
        StartupLogger.log("splitters")
        
        self.body_layout.addWidget(self.activity_bar)
        self.body_layout.addWidget(self.horizontal_splitter, stretch=1)
        
        self.horizontal_splitter.addWidget(self.side_bar)
        self.horizontal_splitter.addWidget(self.central_splitter)
        self.horizontal_splitter.addWidget(self.side_bar_right)
        StartupLogger.log("body_layout_assembled")
        
        # Components & Tabs
        try:
            self.tabs = TabContainer()
            StartupLogger.log("TabContainer")
        except Exception as e:
            StartupLogger.log("TabContainer", e)
            self.tabs = QWidget()
            
        try:
            self.bottom_panel = BottomPanel()
            StartupLogger.log("BottomPanel")
        except Exception as e:
            StartupLogger.log("BottomPanel", e)
            self.bottom_panel = QWidget()
            
        try:
            self.inspector = InspectorPanel() if InspectorPanel else QWidget()
            StartupLogger.log("InspectorPanel")
        except Exception as e:
            StartupLogger.log("InspectorPanel", e)
            self.inspector = QWidget()
        
        # Sidebars setup
        try:
            if hasattr(self.side_bar_right, 'add_panel'):
                # Adicionar explicitamente no índice 0
                self.side_bar_right.add_panel(self.inspector, "AEC Inspector", idx=0)
                # Garantir que o painel 0 seja o exibido
                self.side_bar_right.show_panel(0, "AEC Inspector")
                # Iniciar expandido para visualização imediata do teste
                if SettingsService.instance().get_bool("startup_open_inspector", True):
                    self.side_bar_right.expand()
                else: 
                     self.side_bar_right.collapse()
            StartupLogger.log("sidebar_right_setup")
        except Exception as e:
            StartupLogger.log("sidebar_right_setup", e)

        self.view_stack = QStackedWidget()
        self.view_stack.addWidget(self.tabs)
        StartupLogger.log("view_stack_tabs")
        
        try:
            self.light_table = LightTableView()
            StartupLogger.log("LightTableView")
        except Exception as e:
            StartupLogger.log("LightTableView", e)
            self.light_table = QWidget()
            
        self.view_stack.addWidget(self.light_table)

        self.central_splitter.addWidget(self.view_stack)
        self.central_splitter.addWidget(self.bottom_panel)
        self.central_splitter.setSizes([700, 30])
        StartupLogger.log("central_splitter_setup")
        
        # Add to Main Layout
        self.outer_layout.addWidget(self.top_bar)
        self.outer_layout.addWidget(self.body_container, stretch=1)
        StartupLogger.log("COMPLETE")

    def _setup_connections_v4(self):
        """Conexões modularizadas e resilientes com Lazy Loading."""
        self.tabs.fileChanged.connect(self._on_tab_changed)
        
        # Conexão segura com ActivityBar (conforme diagnóstico)
        if hasattr(self.activity_bar, 'clicked'):
            self.activity_bar.clicked.connect(self._on_activity_clicked)
        
        # Conexões da Sidebar (Thumbnail, etc) são feitas via Lazy Loading em _ensure_panel_loaded
        # para evitar AttributeError no startup.
        
        # Painéis da sidebar serão carregados sob demanda (Lazy Loading)
        self.thumbnails = None
        self.toc_panel = None
        self.search_panel = None
        self.annotations_panel = None

        if hasattr(self.light_table, "pageMoved"):
            self.light_table.pageMoved.connect(self._on_light_table_moved)

        # Atalhos Globais
        self.search_shortcut = QAction("Search", self)
        self.search_shortcut.setShortcut(QKeySequence("Ctrl+F"))
        self.search_shortcut.triggered.connect(self._focus_search)
        self.addAction(self.search_shortcut)

        self.split_shortcut = QAction("Split", self)
        self.split_shortcut.setShortcut(QKeySequence("Ctrl+\\"))
        self.split_shortcut.triggered.connect(self._on_split_clicked)
        self.addAction(self.split_shortcut)

    def _ensure_panel_loaded(self, name: str):
        """Garante que um painel da sidebar esteja carregado (Lazy Loading)."""
        try:
            if name == "thumbnails" and not self.thumbnails:
                self.thumbnails = ThumbnailPanel(adapter=self._adapter, parent=self.side_bar)
                self.thumbnails.pageSelected.connect(lambda idx: self.viewer.scroll_to_page(idx) if self.viewer else None)
                self.thumbnails.orderChanged.connect(self._on_pages_reordered)
                self.side_bar.add_panel(self.thumbnails, "Páginas", idx=0)
                # Nota: load_thumbnails não é chamado aqui, pois o _on_tab_changed ou
                # o click na activity_bar cuidará da sincronização inicial.

            elif name == "search" and not self.search_panel:
                from src.application.use_cases.search_text import SearchTextUseCase
                self.search_panel = SearchPanel(SearchTextUseCase(self._adapter), parent=self.side_bar)
                # CRITICAL: Converter físico -> visual antes de scrollar
                self.search_panel.result_clicked.connect(
                    lambda p_idx, highlights, p_path: self._navigate_to_physical_page(p_path, p_idx, highlights)
                )
                self.side_bar.add_panel(self.search_panel, "Pesquisar", idx=1)
                
                # Sincronização Imediata
                if self.current_file:
                    self.search_panel.set_pdf(self.current_file)

            elif name == "toc" and not self.toc_panel:
                from src.application.use_cases.get_toc import GetTOCUseCase
                self.toc_panel = TOCPanel(GetTOCUseCase(self._adapter), parent=self.side_bar)
                self.toc_panel.bookmark_clicked.connect(
                    lambda p_idx, p_path: self._navigate_to_physical_page(p_path, p_idx)
                )
                self.side_bar.add_panel(self.toc_panel, "Índice", idx=2)
                
                # Sincronização Imediata
                if self.current_file:
                    self.toc_panel.set_pdf(self.current_file)
            
            elif name == "annotations" and not self.annotations_panel:
                from src.interfaces.gui.widgets.annotations_panel import AnnotationsPanel
                from src.infrastructure.repositories.annotation_repository import AnnotationRepository
                from src.application.use_cases.manage_annotations import ManageAnnotationsUseCase
                
                repo = AnnotationRepository()
                use_case = ManageAnnotationsUseCase(repo)
                
                self.annotations_panel = AnnotationsPanel(use_case, parent=self.side_bar)
                self.annotations_panel.annotationClicked.connect(
                    lambda p_idx, aid, p_path: self._navigate_to_physical_page(p_path, p_idx)
                )
                self.side_bar.add_panel(self.annotations_panel, "Notas", idx=3)
                
                # Sincronização Imediata
                if self.current_file:
                    self.annotations_panel.set_pdf(self.current_file)
                
        except Exception as e:
            log_exception(f"Erro ao carregar painel {name}: {e}")
            self.bottom_panel.add_log(f"⚠️ Erro ao carregar painel '{name}': {e}", color="red")


    def _load_settings(self):
        """Carrega as configurações do usuário via conector hexagonal."""
        try:
            if not self._settings_connector:
                from src.infrastructure.adapters.gui_settings_adapter import GUISettingsAdapter
                self._settings_connector = GUISettingsAdapter()

            geometry, state = self._settings_connector.load_window_state()
            if geometry: self.restoreGeometry(geometry)
            if state: self.restoreState(state)
                
            log_debug("MainWindow: Settings carregados via conector.")
        except Exception as e:
            log_exception(f"Erro ao carregar settings: {e}")

    def _save_settings(self):
        """Salva as configurações do usuário via conector hexagonal."""
        try:
            if self._settings_connector:
                self._settings_connector.save_window_state(
                    self.saveGeometry(), 
                    self.saveState()
                )
            log_debug("MainWindow: Settings salvos via conector.")
        except Exception as e:
            log_exception(f"Erro ao salvar settings: {e}")

    def closeEvent(self, event):
        """Salva configurações e encerra processos ao fechar."""
        from src.interfaces.gui.state.render_engine import RenderEngine
        RenderEngine.instance().shutdown()
        
        self._save_settings()
        super().closeEvent(event)

    def _on_light_table_moved(self, *args):
        """Manipula a intenção de reordenação na Mesa de Luz (Debounced)."""
        if not hasattr(self, "_lt_reorder_timer"):
            self._lt_reorder_timer = QTimer(self)
            self._lt_reorder_timer.setSingleShot(True)
            self._lt_reorder_timer.timeout.connect(self._sync_order_from_light_table)
        
        # Iniciar timer de 1.5s - só dispara se o usuário parar de mover
        self._lt_reorder_timer.start(1500)

    def _sync_order_from_light_table(self):
        """Calcula a nova ordem baseada na posição espacial dos itens na Mesa de Luz."""
        if not self.light_table or not self.state_manager:
            return

        from src.interfaces.gui.widgets.light_table_view import PageItem
        items = [i for i in self.light_table.scene.items() if isinstance(i, PageItem)]
        if not items: return

        # Ordenar por posição na cena (Y, X)
        items.sort(key=lambda it: (it.y(), it.x()))

        # Usar identidade estável (Path, Index Original) para a reordenação
        # Isso sobrevive a múltiplas reordenações sem perder a referência
        new_order_identities = [(it.source_path, it.page_index) for it in items]
        
        self._on_pages_reordered(new_order_identities)

    def _on_pages_reordered(self, new_order: list):
        """
        Sincroniza viewer e state com a nova ordem das páginas.
        Suporta tanto lista de índices (int) quanto lista de identidades (tuple).
        """
        if not self.state_manager: return
        
        # 1. Converter identidades para índices se necessário
        if new_order and isinstance(new_order[0], tuple):
            # Mapear identities (path, idx) -> índice atual na lista do state_manager
            # Para isso, precisamos saber onde cada página do state_manager está "agora"
            current_pages = self.state_manager.pages
            id_to_current_idx = {}
            for i, p in enumerate(current_pages):
                # O state_manager guarda o path no doc.name ou similar
                # p.source_doc.name é o caminho absoluto
                id_to_current_idx[(str(p.source_doc.name), p.source_page_index)] = i
            
            # Nova ordem baseada nos índices da lista atual
            new_idx_order = []
            for ident in new_order:
                # Sanitizar ident (garantir que path seja string comparável)
                path_str = str(Path(ident[0]).resolve())
                # Tentar encontrar a página. Se não achar, ignorar (segurança)
                # Nota: a comparação de path pode ser sensível a case em Windows, 
                # mas resolve() ajuda.
                lookup_key = (path_str, ident[1])
                
                # Fallback: tentar match parcial se o path absoluto exato falhar
                if lookup_key not in id_to_current_idx:
                    # Tentar encontrar por basename se necessário
                    pass 

                if lookup_key in id_to_current_idx:
                    new_idx_order.append(id_to_current_idx[lookup_key])
            
            new_order = new_idx_order

        if not new_order: return

        log_debug(f"MainWindow: Aplicando reordenação de índices: {new_order}")
        
        # 2. Atualizar o Gerenciador de Estado
        self.state_manager.reorder_pages(new_order)
        
        # 3. Atualizar o Visualizador
        if self.viewer:
            self.viewer.reorder_pages(new_order)
        
        # 4. Atualizar Thumbnails
        if self.thumbnails:
            # Sincronizar ordens através das identidades do StateManager (Verdade Absoluta)
            # USAR .name (que no fitz.Document é o path completo) em vez de .path
            identities = [(str(p.source_doc.name), p.source_page_index) for p in self.state_manager.pages]
            self.thumbnails.load_thumbnails(identities)

        self.statusBar().showMessage("Ordem das páginas atualizada.", 3000)


    def _on_search_changed(self, text):
        """Intercepta comandos instantâneos conforme o usuário digita."""
        cmd = text.lower().strip()
        # Comandos que queremos disparar na hora (sem Enter)
        instant_triggers = {
            "config": "config", "settings": "settings", "configurações": "configurações",
            "ia": "ia", "ai": "ai", 
            "mesa": "mesa", "scroll": "scroll"
        }
        
        if cmd in instant_triggers:
            # Feedback na status bar para confirmar detecção
            self.statusBar().showMessage(f"⚡ Comando detectado: {cmd}", 2000)
            self._on_search_triggered(text)
            # Opcional: Limpar o campo para permitir próxima digitação
            if hasattr(self.top_bar, 'search_input'):
                 self.top_bar.search_input.clear()

    def _on_search_triggered(self, query):
        """Orquestração inteligente da busca superior (Universal Search + Command Palette)."""
        from src.interfaces.gui.utils.ui_error_boundary import safe_ui_callback
        
        @safe_ui_callback("Command/Search Palette")
        def _execute():
            # 1. Verificar se é um comando interno (Command Palette)
            cmd_lower = query.lower().strip()
            
            # Map de comandos amigáveis (Internacionalização/Variantes)
            commands = {
                "configurações": self._on_startup_config_clicked,
                "config": self._on_startup_config_clicked,
                "diagnóstico": self._on_startup_config_clicked,
                "settings": self._on_startup_config_clicked,
                "ia": self._on_ai_settings_clicked,
                "ai": self._on_ai_settings_clicked,
                "miniaturas": lambda: self._on_activity_clicked(0),
                "explorer": lambda: self._on_activity_clicked(0),
                "busca": lambda: self._on_activity_clicked(1),
                "sumário": lambda: self._on_activity_clicked(2),
                "toc": lambda: self._on_activity_clicked(2),
                "mesa de luz": lambda: self._switch_view_mode_v4("table"),
                "mesa": lambda: self._switch_view_mode_v4("table"),
                "scroll": lambda: self._switch_view_mode_v4("scroll"),
                "leitura": lambda: self._switch_view_mode_v4("scroll"),
                "abrir": self._on_open_clicked,
                "unir": self._on_merge_clicked,
                "merge": self._on_merge_clicked,
                "ajuda": lambda: self.statusBar().showMessage("Comandos: config, ia, mesa, scroll, abrir, unir", 5000)
            }
            
            if cmd_lower in commands:
                self.bottom_panel.add_log(f"⌨️ Executando comando: {cmd_lower}")
                commands[cmd_lower]()
                return

            # 2. Se não for comando, delegar para o Orchestrator (IA / Busca de Texto)
            if hasattr(self, 'orchestrator'):
                 response = self.orchestrator.execute(query, self.current_file)
                 self._handle_orchestrator_response(query, response)
            else:
                 # Fallback: Se não tem orchestrator, tenta busca de texto básica
                 self.bottom_panel.add_log(f"🔎 Pesquisando por: {query}")
                 # Se o painel de busca estiver carregado, use-o
                 self._on_activity_clicked(1) # Abre aba de busca
        
        _execute()

    def _handle_orchestrator_response(self, query, response):
        """Processa a resposta do orquestrador de busca."""
        if response["type"] == "command":
            self.bottom_panel.add_log(f"⚡ [CMD] {response.get('message')}")
            if "path" in response:
                self.open_file(Path(response["path"]))
        elif response["type"] == "search":
            if hasattr(self.activity_bar, 'set_active'):
                self.activity_bar.set_active(1)
            if self.search_panel:
                self.search_panel.set_results(response["results"])
            self.bottom_panel.add_log(f"🔎 Encontradas {len(response['results'])} ocorrências para '{query}'")
        elif response["type"] == "error":
            self.bottom_panel.add_log(f"❌ {response.get('message')}", color="red")

    def _on_layout_toggle_requested(self, target):
        """Responde aos botões de toggle da TopBar."""
        if target == "sidebar_left":
            self.side_bar.toggle_collapse()
        elif target == "sidebar_right":
            self.side_bar_right.toggle_collapse()
        elif target == "bottom_panel":
            self.bottom_panel.toggle_expand()

    def _switch_view_mode_v4(self, mode):
        idx = 0 if mode == "scroll" else 1
        self.view_stack.setCurrentIndex(idx)
        
        # Sincronizar NavBar Moderna com a visão ativa
        if mode == "table" and hasattr(self.light_table, "setup_nav_bar"):
            # A navbar é interna ao visualizador (viewer_left), mas podemos 
            # compartilhá-la ou usar a do viewer_left como mestre.
            # Aqui, vinculamos a barra do visualizador atual à lógica da mesa.
            viewer = self.viewer # PDFViewerWidget ativo
            if viewer and hasattr(viewer, "nav_bar"):
                self.light_table.setup_nav_bar(viewer.nav_bar)
        
        # Garantir que o visualizador receba foco para atalhos de teclado funcionarem
        if self.view_stack.currentWidget():
            self.view_stack.currentWidget().setFocus()
            
        self.bottom_panel.add_log(f"🔄 Modo de visualização alterado para: {mode.upper()}")
    
    def keyPressEvent(self, event):
        """Atalhos globais da aplicação."""
        if event.modifiers() == Qt.KeyboardModifier.ShiftModifier and event.key() == Qt.Key.Key_N:
            # Toggle global do NavHub no visualizador ativo
            widget = self.view_stack.currentWidget()
            if hasattr(widget, "nav_hub"):
                if widget.nav_hub.isVisible(): widget.nav_hub.hide()
                else: widget.nav_hub.show()
                if hasattr(widget, "_update_nav_pos"):
                    widget._update_nav_pos()
            return
            
        super().keyPressEvent(event)

    def _switch_view_mode(self, index):
        """Alterna entre ScrollView e LightTable."""
        self.view_stack.setCurrentIndex(index)
        self.btn_scroll_view.setChecked(index == 0)
        self.btn_light_table.setChecked(index == 1)
        mode_name = "Modo Leitura (Scroll)" if index == 0 else "Modo Mesa de Luz"
        self.statusBar().showMessage(f"Alternado para: {mode_name}", 3000)
    
    def _toggle_bottom_panel(self):
        """Toggle para o painel inferior."""
        if self.bottom_panel.height() < 50:
            # Expandir
            self.central_splitter.setSizes([600, 200])
            self.btn_toggle_panel.setText("▼ Comandos")
        else:
            # Colapsar
            self.central_splitter.setSizes([800, 0])
            self.btn_toggle_panel.setText("▲ Comandos")

    def _setup_window_icon(self):
        icon_path = ResourceService.get_logo_ico()
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))


    def _setup_menus(self):
        """Creates a cascading popup menu (no native menubar) - REFACTORED V2 (Lúdico)."""
        from PyQt6.QtWidgets import QMenu
        
        # Hide the native menu bar for Chrome-less UI
        self.menuBar().setVisible(False)
        
        # Create the master popup menu
        self.app_menu = QMenu(self)
        self.app_menu.setObjectName("AppMenu")
        self.app_menu.setStyleSheet("""
            QMenu {
                background-color: #27272A;
                border: 1px solid #3F3F46;
                border-radius: 8px;
                padding: 8px 0;
            }
            QMenu::item {
                padding: 8px 24px;
                color: #E2E8F0;
                font-size: 13px;
                font-weight: 500;
            }
            QMenu::item:selected {
                background-color: #3F3F46;
                color: #FFD600;
            }
            QMenu::separator {
                height: 1px;
                background: #3F3F46;
                margin: 4px 12px;
            }
        """)
        
        # --- 📂 ARQUIVO & PROJETO ---
        file_menu = self.app_menu.addMenu("📂 Arquivos")
        file_menu.addAction("Abrir PDF...").triggered.connect(self._on_open_clicked)
        file_menu.addAction("Unir PDFs (Merge)...").triggered.connect(self._on_merge_clicked)
        
        self.save_action = file_menu.addAction("Salvar Alterações")
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.setEnabled(False)
        self.save_action.triggered.connect(self._on_save_clicked)
        
        self.save_as_action = file_menu.addAction("Salvar Como...")
        self.save_as_action.setShortcut("Ctrl+Shift+S")
        self.save_as_action.setEnabled(False)
        self.save_as_action.triggered.connect(self._on_save_as_clicked)
        
        file_menu.addSeparator()
        
        export_menu = file_menu.addMenu("📤 Exportar...")
        export_menu.addAction("Imagem (PNG High-DPI)").triggered.connect(lambda: self._on_export_image_clicked("png"))
        export_menu.addAction("Vetor (SVG)").triggered.connect(self._on_export_svg_clicked)
        export_menu.addAction("Documento (Markdown)").triggered.connect(self._on_export_md_clicked)
        
        # --- 🛠️ FERRAMENTAS DE EDIÇÃO ---
        edit_menu = self.app_menu.addMenu("🛠️ Edição e Manipulação")
        
        edit_menu.addAction("Desfazer (Undo)").triggered.connect(self._undo_action)
        edit_menu.addAction("Refazer (Redo)").triggered.connect(self._redo_action)
        
        edit_menu.addSeparator()
        
        rot_menu = edit_menu.addMenu("🔄 Rotação")
        self.rotate_left_action = rot_menu.addAction("Girar Esquerda (-90°)")
        self.rotate_left_action.triggered.connect(lambda: self._on_rotate_clicked(-90))
        
        self.rotate_right_action = rot_menu.addAction("Girar Direita (+90°)")
        self.rotate_right_action.triggered.connect(lambda: self._on_rotate_clicked(90))
        
        edit_menu.addSeparator()
        
        self.extract_action = edit_menu.addAction("📄 Extrair Páginas Selecionadas")
        self.extract_action.setEnabled(False)
        self.extract_action.triggered.connect(self._on_extract_clicked)
        
        # --- 🧠 INTELIGÊNCIA ARTIFICIAL ---
        ai_menu = self.app_menu.addMenu("🧠 Inteligência Artificial")
        
        ai_menu.addAction("⚙️ Configurar Assistente...").triggered.connect(self._on_ai_settings_clicked)
        
        self.ocr_area_action = ai_menu.addAction("🎯 OCR por Área (Seleção)")
        self.ocr_area_action.setCheckable(True)
        self.ocr_area_action.triggered.connect(self._on_ocr_area_toggled)
        
        # --- 🎨 APARÊNCIA & LAYOUT ---
        view_menu = self.app_menu.addMenu("🎨 Aparência")
        
        theme_menu = view_menu.addMenu("🌗 Tema de Leitura")
        theme_menu.addAction("Padrão (Dark Grey)").triggered.connect(lambda: self.viewer.set_reading_mode("default") if self.viewer else None)
        theme_menu.addAction("Sépia (Conforto)").triggered.connect(lambda: self.viewer.set_reading_mode("sepia") if self.viewer else None)
        theme_menu.addAction("Noturno (OLED)").triggered.connect(lambda: self.viewer.set_reading_mode("dark") if self.viewer else None)

        view_menu.addSeparator()

        layout_menu = view_menu.addMenu("🔲 Layout")
        self.layout_action = layout_menu.addAction("Lado a Lado (Dual Page)")
        self.layout_action.setCheckable(True)
        self.layout_action.triggered.connect(self._on_layout_toggled)
        
        self.split_action = layout_menu.addAction("Dividir Editor (Split View)")
        self.split_action.triggered.connect(self._on_split_clicked)

        # --- 🧭 NAVEGAÇÃO ---
        nav_menu = self.app_menu.addMenu("🧭 Navegação")
        self.back_action = nav_menu.addAction("Voltar (Histórico)")
        self.back_action.setShortcut(QKeySequence.StandardKey.Back)
        self.back_action.triggered.connect(self._on_back_clicked)
        self.back_action.setEnabled(False)

        self.forward_action = nav_menu.addAction("Avançar (Histórico)")
        self.forward_action.setShortcut(QKeySequence.StandardKey.Forward)
        self.forward_action.triggered.connect(self._on_forward_clicked)
        self.forward_action.setEnabled(False)
        
        # --- ⚙️ SISTEMA ---
        sys_menu = self.app_menu.addMenu("⚙️ Sistema")
        sys_menu.addAction("🚀 Inicialização e Performance...").triggered.connect(self._on_startup_config_clicked)
        sys_menu.addAction("🔍 Diagnóstico de Recursos").triggered.connect(lambda: self.statusBar().showMessage("Diagnóstico iniciado...", 2000))


    def _on_ai_settings_clicked(self):
        """Abre o painel de configurações de IA em um diálogo modal."""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout
        from src.interfaces.gui.widgets.ai_settings_panel import AISettingsWidget
        
        dlg = QDialog(self)
        dlg.setWindowTitle("Configuração da Inteligência Artificial")
        dlg.setMinimumSize(500, 600)
        
        layout = QVBoxLayout(dlg)
        settings_widget = AISettingsWidget(dlg)
        layout.addWidget(settings_widget)
        
        dlg.exec()

    def _on_startup_config_clicked(self):
        """Abre o diálogo de configuração de inicialização."""
        from src.interfaces.gui.widgets.startup_config import StartupConfigDialog
        from PyQt6.QtWidgets import QMessageBox
        
        dlg = StartupConfigDialog(self)
        if dlg.exec():
            dlg.save_settings()
            QMessageBox.information(self, "Configuração Salva", "As alterações terão efeito na próxima reinicialização.")

    def _setup_statusbar(self):
        from PyQt6.QtWidgets import QPushButton, QHBoxLayout, QFrame
        
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Pronto")
        
        # Container para botões de toggle (Layout) na direita
        self.status_controls = QWidget()
        layout = QHBoxLayout(self.status_controls)
        layout.setContentsMargins(0, 0, 5, 0)
        layout.setSpacing(2)
        
        # Botão Toggle SideBar (Left)
        self.btn_toggle_sidebar = QPushButton("▥")
        self.btn_toggle_sidebar.setToolTip("Alternar Left Side Bar")
        self.btn_toggle_sidebar.setFixedSize(24, 20)
        self.btn_toggle_sidebar.setStyleSheet("background: transparent; border: none; color: #858585;")
        if hasattr(self.side_bar, 'toggle_collapse'):
            self.btn_toggle_sidebar.clicked.connect(self.side_bar.toggle_collapse)
        
        # Botão Toggle Bottom Panel
        self.btn_toggle_bottom = QPushButton("▃")
        self.btn_toggle_bottom.setToolTip("Alternar Painel Inferior")
        self.btn_toggle_bottom.setFixedSize(24, 20)
        self.btn_toggle_bottom.setStyleSheet("background: transparent; border: none; color: #858585;")
        self.btn_toggle_bottom.clicked.connect(self.bottom_panel.toggle_expand)

        # Botão Toggle Right SideBar
        self.btn_toggle_right = QPushButton("▤")
        self.btn_toggle_right.setToolTip("Alternar Right Side Bar")
        self.btn_toggle_right.setFixedSize(24, 20)
        self.btn_toggle_right.setStyleSheet("background: transparent; border: none; color: #858585;")
        if hasattr(self.side_bar_right, 'toggle_collapse'):
            self.btn_toggle_right.clicked.connect(self.side_bar_right.toggle_collapse)
        
        # Botão Toggle ActivityBar
        self.btn_toggle_activity = QPushButton("┇")
        self.btn_toggle_activity.setToolTip("Alternar Activity Bar")
        self.btn_toggle_activity.setFixedSize(24, 20)
        self.btn_toggle_activity.setStyleSheet("background: transparent; border: none; color: #858585;")
        if hasattr(self.activity_bar, 'setVisible'):
            self.btn_toggle_activity.clicked.connect(self._on_toggle_activity_bar)
        
        layout.addWidget(self.btn_toggle_sidebar)
        layout.addWidget(self.btn_toggle_bottom)
        layout.addWidget(self.btn_toggle_right)
        layout.addWidget(self.btn_toggle_activity)
        
        self.statusBar().addPermanentWidget(self.status_controls)

    def _on_toggle_activity_bar(self):
        """Alterna a visibilidade da barra de atividades."""
        visible = self.activity_bar.isVisible()
        self.activity_bar.setVisible(not visible)

    @safe_ui_callback("Tab Switch")
    def _on_tab_changed(self, file_path):
        """Sincroniza a UI quando o usuário muda de aba."""
        try:
            if not file_path:
                # Se não há arquivo (todas as abas fechadas), limpar painéis
                log_debug("MainWindow [TAB_CHANGED]: Nenhum arquivo ativo. Limpando painéis.")
                self.setWindowTitle("fotonPDF")
                self.current_file = None
                
                if self.thumbnails: self.thumbnails.load_thumbnails([])
                if self.toc_panel: self.toc_panel.set_pdf(None)
                if self.search_panel: self.search_panel.set_pdf(None)
                if self.inspector: self.inspector.update_metadata(None)
                if hasattr(self, 'light_table') and self.light_table: 
                    self.light_table.clear()
                return
            log_debug("MainWindow [TAB_CHANGED]: Iniciando sincronização...")
            
            self.current_file = file_path
            self.setWindowTitle(f"fotonPDF - {file_path.name}")
            
            # Obter metadados via CACHE ou Fallback Vazio (Non-blocking)
            group = self.tabs.current_editor()
            if not group or not group.metadata:
                log_debug(f"MainWindow: Metadados ausentes para {file_path.name}. Usando fallback vazio.")
                metadata = {"page_count": 0, "pages": [], "layers": []}
            else:
                metadata = group.metadata
            
            # EMERGENCY FIX: Se o viewer existe mas está vazio, forçar reload
            if group and hasattr(group, 'viewer_left') and group.viewer_left:
                viewer = group.viewer_left
                if hasattr(viewer, '_pages') and len(viewer._pages) == 0:
                    log_debug(f"MainWindow [EMERGENCY]: ViewerWidget vazio! Forçando reload...")
                    # Construir metadata de emergência a partir do StateManager se possível
                    if self.state_manager and self.state_manager.pages:
                        doc = self.state_manager.pages[0].source_doc
                        page_count = len(self.state_manager.pages)
                        rescue_metadata = {
                            "page_count": page_count,
                            "pages": [{"width_mm": 210, "height_mm": 297, "format": "A4"} for _ in range(page_count)],
                            "layers": []
                        }
                        log_debug(f"MainWindow [EMERGENCY]: Metadados resgatados: {page_count} páginas")
                        viewer.load_document(file_path, rescue_metadata)
                        group.metadata = rescue_metadata  # Atualizar cache do group
                        metadata = rescue_metadata
            
            log_debug("MainWindow [TAB_CHANGED]: [1/5] Metadados obtidos.")
            
            # Sincronizar painéis laterais (Lazy Sync)
            # Cada um em seu bloco try-except para evitar cascade failure
            
            # FORÇA carregamento do ThumbnailPanel se ainda não foi carregado
            if not self.thumbnails:
                self._ensure_panel_loaded("thumbnails")
            
            if self.thumbnails:
                try:
                    # Preferencialmente usar identidades se o state_manager estiver pronto
                    if self.state_manager:
                        # USAR .name (Path completo no fitz) para evitar desvio no RenderEngine
                        identities = [(str(p.source_doc.name), p.source_page_index) for p in self.state_manager.pages]
                        self.thumbnails.load_thumbnails(identities)
                    else:
                        # Fallback seguro
                        ids = [(str(file_path), i) for i in range(metadata.get("page_count", 0))]
                        self.thumbnails.load_thumbnails(ids)
                except Exception as e:
                    log_exception(f"MainWindow: Falha ao atualizar Thumbnails: {e}")
            log_debug("MainWindow [TAB_CHANGED]: [2/5] Thumbnails OK.")

            
            if self.toc_panel:
                try:
                    self.toc_panel.set_pdf(file_path)
                except Exception as e:
                    log_exception(f"MainWindow: Falha ao atualizar TOC: {e}")
            log_debug("MainWindow [TAB_CHANGED]: [3/5] TOC OK.")
            
            # Sincronizar SearchPanel com o documento ativo
            if self.search_panel:
                try:
                    self.search_panel.set_pdf(file_path)
                except Exception as e:
                    log_exception(f"MainWindow: Falha ao atualizar Search: {e}")
            log_debug("MainWindow [TAB_CHANGED]: [3.5/5] Search OK.")

                
            if self.inspector and hasattr(self.inspector, 'update_metadata'):
                try:
                    self.inspector.update_metadata(metadata)
                except Exception as e:
                    log_exception(f"MainWindow: Falha ao atualizar Inspector: {e}")
            log_debug("MainWindow [TAB_CHANGED]: [4/5] Inspector OK.")
            
            # Sincronizar Mesa de Luz (LightTable)
            if hasattr(self, 'light_table') and self.light_table:
                try:
                    self.light_table.load_document(file_path, metadata)
                except Exception as e:
                    log_exception(f"MainWindow: Falha ao atualizar Mesa de Luz: {e}")
            log_debug("MainWindow [TAB_CHANGED]: [4.5/5] LightTable OK.")
            
            # Sincronizar conexões do visualizador ativo
            if self.viewer:
                try:
                    try: self.viewer.pageChanged.disconnect()
                    except: pass
                    try: self.viewer.selectionChanged.disconnect()
                    except: pass
                    try: self.viewer.statusMessageRequested.disconnect()
                    except: pass
                    # Nota: Não desconectamos nav_bar aqui pois é interna do viewer, mas ok.
                    
                    self.viewer.pageChanged.connect(self._on_page_changed, Qt.ConnectionType.UniqueConnection)
                    # Conectar seleção à telemetria (MM)
                    self.viewer.selectionChanged.connect(self._on_selection_changed, Qt.ConnectionType.UniqueConnection)
                    self.viewer.nav_bar.toggleSplit.connect(self._on_split_clicked, Qt.ConnectionType.UniqueConnection)
                    
                    # Feedback Visual (Status Bar)
                    self.viewer.statusMessageRequested.connect(lambda msg, ms: self.statusBar().showMessage(msg, ms))
                    
                    # Conectar Draft Note
                    try: self.viewer.draftNoteRequested.disconnect()
                    except: pass
                    self.viewer.draftNoteRequested.connect(self._on_draft_note_requested)
                    
                    # Conectar Highlight (Persistence)
                    try: self.viewer.highlightRequested.disconnect()
                    except: pass
                    self.viewer.highlightRequested.connect(self._on_highlight_requested)
                    
                    # Focar visualizador para atalhos imediatos
                    self.viewer.setFocus()
                except (TypeError, RuntimeError): 
                    pass
                except Exception as e:
                     log_exception(f"MainWindow: Falha ao conectar sinais do Viewer: {e}")
            
            # Conectar Inspector à porta de camadas
            try:
                # Necessário desconectar anterior? UniqueConnection resolve.
                # Verificar se inspector é realmente um InspectorPanel (não um fallback QWidget)
                if self.inspector and hasattr(self.inspector, 'layerVisibilityChanged'):
                     self.inspector.layerVisibilityChanged.connect(
                        lambda lid, vis: self._on_layer_toggle(file_path, lid, vis),
                        Qt.ConnectionType.UniqueConnection
                    )
            except Exception as e:
                log_exception(f"MainWindow: Falha ao conectar Inspector Layers: {e}")
            log_debug("MainWindow [TAB_CHANGED]: [5/5] Conexões completas.")
            
            if hasattr(self, 'bottom_panel'):
                try:
                    self.bottom_panel.add_log(f"Synced Meta for: {file_path.name}")
                except: pass
                
            # Sincronizar o contador de páginas na mesa de luz no início da sessão
            if hasattr(self, 'light_table') and hasattr(self.light_table, 'update_page'):
                 current_idx = self.viewer.get_current_page_index() if self.viewer else 0
                 self.light_table.update_page(current_idx, metadata.get("page_count", 0))

        except Exception as e:
             log_exception(f"MainWindow: Erro Crítico em _on_tab_changed: {e}")
             # Não propagar para evitar crash da GUI

    def _on_activity_clicked(self, idx):
        # Fail-safe: Se side_bar ou activity_bar forem dummy widgets, mostrar fallback visual
        if not hasattr(self.side_bar, 'stack') or not hasattr(self.activity_bar, 'group'):
            self.bottom_panel.add_log(f"ℹ️ Sidebar desativada. Ative-a em Ajustes > Inicialização.")
            return

        titles = {0: "PÁGINAS", 1: "PESQUISAR", 2: "ÍNDICE", 3: "NOTAS"}
        
        # SPECIAL: Settings icon (99) opens the app menu popup
        if idx == 99:
            # Position the menu near the settings button in ActivityBar
            settings_btn = self.activity_bar.group.button(99)
            if settings_btn:
                pos = settings_btn.mapToGlobal(settings_btn.rect().topRight())
                self.app_menu.exec(pos)
            return
        
        # Lazy Loading: Garantir que o painel selecionado esteja carregado
        if idx == 0: self._ensure_panel_loaded("thumbnails")
        elif idx == 1: self._ensure_panel_loaded("search")
        elif idx == 2: self._ensure_panel_loaded("toc")
        elif idx == 3: self._ensure_panel_loaded("annotations")

        target_idx = idx
        
        # Se clicar no ícone que já está ativo e a sidebar estiver aberta, colapsa.
        # Caso contrário (estiver fechada ou for outro ícone), garante a abertura e atualização.
        is_already_active = self.side_bar.stack.currentIndex() == target_idx
        
        if is_already_active and not self.side_bar._is_collapsed:
            self.side_bar.toggle_collapse()
        else:
            self.side_bar.show_panel(target_idx, titles.get(target_idx, "SIDEBAR"))


    def _on_search_results_found(self, results):
        """Atualiza os marcadores na barra de rolagem."""
        if not self.state_manager: return
        
        page_count = self.state_manager.get_page_count()
        if page_count == 0: return
        
        # Calcular posições relativas (0.0 a 1.0)
        positions = [res.page_index / page_count for res in results]
        
        # Definir marcadores na scrollbar do viewer
        self.viewer.verticalScrollBar().set_markers(positions)

    @safe_ui_callback("Open File")
    def open_file(self, file_path: Path):
        """Inicia o carregamento do documento (Síncrono ou Assíncrono conforme config). Pipolote """
        # 0. Iniciar nova sessão de log para correlação (Debug Conjunto)
        from src.infrastructure.services.logger import set_session_id
        session = set_session_id()
        log_debug(f"MainWindow: Iniciando tentativa de abertura: {session} para {file_path.name}")
        
        TelemetryService.mark_start("TTU")
        file_path = Path(file_path).resolve()
        if not file_path.exists():
            self.statusBar().showMessage(f"Erro: Arquivo não encontrado", 3000)
            return

        self.statusBar().showMessage(f"Analisando {file_path.name}...")
        self.setCursor(Qt.CursorShape.WaitCursor)
        self.current_file = file_path # Set immediately to avoid race conditions in UI

        # Verificar preferência de carregamento via Settings
        use_async = SettingsService.instance().get_bool("startup_async_loader", True)

        if use_async:
            # Modo Assíncrono (Padrão)
            self._loader = AsyncDocumentLoader(file_path, self._get_metadata_use_case, self._detect_ocr_use_case)
            self._loader.finished.connect(self._on_load_finished)
            self._loader.progress.connect(lambda msg: self.statusBar().showMessage(msg))
            self._loader.error.connect(self._on_load_error)
            self._loader.start()
        else:
            # Modo Síncrono (Fallback de Segurança / Debug)
            try:
                log_debug(f"MainWindow: Carregando {file_path.name} em modo SÍNCRONO.")
                
                # 1. Abertura do Documento PRIMEIRO (para passar handle ao use case)
                import fitz
                opened_doc = fitz.open(file_path)
                
                # 2. Análise de Metadados COM handle injetado (evita dupla abertura)
                metadata = self._get_metadata_use_case.execute(file_path, doc_handle=opened_doc)
                hints = {"complexity": "STANDARD"}
                metadata["hints"] = hints  # Anexar hints ao metadata para consistência
                is_searchable = True  # Assume true no modo simples
                
                log_debug(f"MainWindow: Sync metadata extraído: page_count={metadata.get('page_count', 0)}")
                
                # 3. Finalização Direta
                self._on_load_finished(file_path, metadata, hints, opened_doc, is_searchable)
            except Exception as e:
                self._on_load_error(str(e))

    @safe_ui_callback("Load Finished")
    def _on_load_finished(self, file_path: Path, metadata: dict, hints: dict, opened_doc, is_searchable: bool):
        """Callback quando o documento e metadados estão prontos. Delegado ao Controller."""
        if hasattr(self, 'workspace_controller'):
            self.workspace_controller.handle_load_finished(file_path, metadata, hints, opened_doc, is_searchable)
        else:
             log_error("CRITICAL: WorkspaceController not initialized!")

    def _on_load_error(self, message: str):
        """Callback em caso de falha no carregamento."""
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.statusBar().showMessage(f"Erro ao abrir arquivo", 5000)
        log_error(f"MainWindow Loader Error: {message}")
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.critical(self, "Erro ao Abrir", f"Não foi possível abrir o documento:\n{message}")

    @safe_ui_callback("Page Change")
    def _on_page_changed(self, index: int):
        """Sincroniza a seleção da sidebar com a página atual do viewer."""
        if self.thumbnails and hasattr(self.thumbnails, 'set_selected_page'):
            self.thumbnails.set_selected_page(index)
            
        # Atualizar telemetria com as dimensões da página atual (sem seleção ativa)
        if hasattr(self, 'bottom_panel') and self.tabs:
            editor = self.tabs.current_editor()
            if editor and editor.metadata:
                pages = editor.metadata.get("pages", [])
                if 0 <= index < len(pages):
                    page_meta = pages[index]
                    self.bottom_panel.update_telemetry(
                        page_meta.get("width_mm", 0),
                        page_meta.get("height_mm", 0),
                        -1, -1 # Indica sem seleção
                    )

        if self._is_navigating_history:
            return
            
        # Sincronizar o contador de páginas na mesa de luz também
        if hasattr(self, 'light_table') and hasattr(self.light_table, 'update_page'):
             page_count = 0
             group = self.tabs.current_editor()
             if group and group.metadata:
                 page_count = group.metadata.get("page_count", 0)
             self.light_table.update_page(index, page_count)
            
    def _on_selection_changed(self, rect_pts: tuple):
        """Converte seleção em pontos para milímetros e atualiza telemetria."""
        from src.domain.services.geometry_service import GeometryService
        dims = GeometryService.get_rect_dimensions_mm(rect_pts)
        self.bottom_panel.update_telemetry(
            dims["width_mm"], dims["height_mm"],
            dims["center_x_mm"], dims["center_y_mm"]
        )


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

    @safe_ui_callback("Save PDF")
    def _on_save_clicked(self):
        """Sobrescreve o arquivo atual."""
        if not self.state_manager or not self.current_file: return
        try:
            self.state_manager.save(str(self.current_file))
            self.statusBar().showMessage(f"Arquivo salvo: {self.current_file.name}")
        except Exception as e:
            self.statusBar().showMessage(f"Erro ao salvar: {e}")

    @safe_ui_callback("Save PDF As")
    def _on_save_as_clicked(self):
        """Salva o estado atual em um novo local."""
        if not self.state_manager: return
        file_path, _ = QFileDialog.getSaveFileName(self, "Salvar PDF Como", "", "Arquivos PDF (*.pdf)")
        if file_path:
            self.state_manager.save(file_path)
            self.statusBar().showMessage(f"Salvo como: {Path(file_path).name}")


    @safe_ui_callback("Export Image")
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

    @safe_ui_callback("Export SVG")
    def _on_export_svg_clicked(self, *args):
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

    @safe_ui_callback("Export Markdown")
    
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

    @safe_ui_callback("Extract Pages")
    def _on_extract_clicked(self, *args):
        """Extrai páginas selecionadas para um novo PDF."""
        if not self.state_manager: return
        
        # Obter índices das páginas selecionadas na sidebar
        selected_rows = []
        if self.thumbnails:
            selected_rows = self.thumbnails.get_selected_rows()
            
        if not selected_rows:
            self.statusBar().showMessage("Selecione páginas na barra lateral para extrair.", 3000)
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Extrair Páginas Selecionadas", 
            "extracao_foton.pdf", 
            "Arquivos PDF (*.pdf)"
        )
        
        if not file_path:
            return

        try:
            self.setCursor(Qt.CursorShape.WaitCursor)
            # Salva o subconjunto baseado na ordem virtual atual
            self.state_manager.save(file_path, indices=selected_rows)
            self.statusBar().showMessage(f"Extraídas {len(selected_rows)} páginas para {Path(file_path).name}", 5000)
            if hasattr(self, 'bottom_panel'):
                self.bottom_panel.add_log(f"Extracted {len(selected_rows)} pages to {Path(file_path).name}")
        except Exception as e:
            log_exception(f"Extraction failed: {e}")
            self.statusBar().showMessage(f"Erro ao extrair páginas: {e}", 5000)
        finally:
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def _on_open_clicked(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Abrir PDF", "", "Arquivos PDF (*.pdf)")
        if file_path:
            self.open_file(Path(file_path))

    def _on_merge_clicked(self):
        """Abre diálogo para unir múltiplos arquivos."""
        files, _ = QFileDialog.getOpenFileNames(self, "Unir PDFs", "", "Arquivos PDF (*.pdf)")
        if files:
            for f in files:
                self._append_pdf(Path(f))
            self.statusBar().showMessage(f"{len(files)} arquivos anexados.", 3000)

    @safe_ui_callback("Append PDF")
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
            # Fix: Pass current session_id to append_thumbnails
            current_session = self.thumbnails._current_session if self.thumbnails else 0
            self.thumbnails.append_thumbnails(str(path), metadata["page_count"], current_session)
            self.statusBar().showMessage(f"Adicionado: {path.name}")
        except Exception as e:
            log_exception(f"MainWindow: Erro ao anexar: {e}")
            self.statusBar().showMessage(f"Erro ao anexar arquivo: {e}")

    @safe_ui_callback("Rotate Page")
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

    @safe_ui_callback("Split Editor")
    def _on_split_clicked(self):
        """Ativa/Desativa o modo Split Editor Assíncrono para o mesmo documento."""
        editor_group = self.tabs.current_editor()
        if editor_group:
            editor_group.toggle_split()
            self.statusBar().showMessage("Split Editor Assíncrono (mesmo documento) alternado.")
            self.bottom_panel.add_log("Toggled Async Split.")

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

    def _apply_ocr_status(self, file_path: Path, is_searchable: bool):
        """Aplica o status de OCR já calculado em background."""
        try:
            has_engine = self._adapter.is_engine_available()
            group = self.current_editor_group
            if not group: return
 
            if not is_searchable and has_engine:
                group.ocr_banner.show()
                # Desconectar antes para evitar duplicidade em recargas
                try: group.btn_apply_ocr.clicked.disconnect()
                except: pass
                group.btn_apply_ocr.clicked.connect(self._on_apply_ocr_clicked)
                self.bottom_panel.add_log(f"OCR needed for {file_path.name}")
            else:
                group.ocr_banner.hide()
        except Exception as e:
            log_exception(f"OCR UI Update: {e}")

    @safe_ui_callback("Apply OCR")
    def _on_apply_ocr_clicked(self):
        """Executa o OCR no documento inteiro."""
        if not self.current_file: return
        
        group = self.current_editor_group
        if not group: return

        group.btn_apply_ocr.setEnabled(False)
        group.btn_apply_ocr.setText("Processando...")
        self.statusBar().showMessage("Executando OCR no documento... Isso pode levar alguns minutos.")
        
        QTimer.singleShot(100, self._process_ocr)

    def _process_ocr(self):
        try:
            new_path = self._apply_ocr_use_case.execute(self.current_file)
            group = self.current_editor_group
            if group: group.ocr_banner.hide()
            
            self.statusBar().showMessage(f"OCR Concluído! Novo arquivo: {new_path.name}")
            self.bottom_panel.add_log(f"OCR successful: {new_path.name}")
            
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
            group = self.current_editor_group
            if group:
                group.btn_apply_ocr.setEnabled(True)
                group.btn_apply_ocr.setText("Aplicar OCR")

    def _on_ocr_area_toggled(self, checked: bool):
        self.viewer.set_selection_mode(checked)
        if checked:
            self.statusBar().showMessage("Modo de Seleção OCR Ativo: Desenhe um retângulo sobre o texto na imagem.")
        else:
            self.statusBar().showMessage("Modo de Seleção OCR Desativado.")

    @safe_ui_callback("Layout Toggle")
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

    @safe_ui_callback("OCR Area")
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

    def _on_draft_note_requested(self, text: str):
        """Receives text from selection and sends to annotations panel as draft."""
        log_debug(f"MainWindow: Recebido pedido de Draft Note: {len(text)} chars")
        
        # 1. Ensure Activity Bar is visible
        if hasattr(self, 'activity_bar') and not self.activity_bar.isVisible():
             self.activity_bar.setVisible(True)
        
        # 2. Activate Notes Tab (Index 3) - Use correct method name
        if hasattr(self.activity_bar, 'set_active'):
            self.activity_bar.set_active(3)
        elif hasattr(self.activity_bar, 'set_active_index'):
            self.activity_bar.set_active_index(3)
        
        # 3. Force load annotations panel (correct name)
        self._ensure_panel_loaded("annotations")
        
        # 4. Inject Text using correct attribute
        if hasattr(self, 'annotations_panel') and self.annotations_panel:
            # Get current page if available
            current_page = 0
            if self.viewer and hasattr(self.viewer, 'current_page_index'):
                current_page = self.viewer.current_page_index
            
            self.annotations_panel.add_annotation(current_page, text)
            log_debug(f"MainWindow: Nota adicionada na página {current_page}")
        else:
            log_warning("MainWindow: annotations_panel não disponível para draft.")

    def _on_highlight_requested(self, page_idx: int, rect: tuple, color: tuple):
        """Handler para criação de Highlights via menu de contexto. Resolve pg virtual para física."""
        log_debug(f"MainWindow: Highlight solicitado na pg visual {page_idx}")
        
        if not self.current_file or not self.state_manager: return

        # 1. Resolver a página virtual para a origem física real
        virtual_page = self.state_manager.get_page(page_idx)
        if not virtual_page:
            log_error(f"MainWindow: Falha ao resolver pg virtual {page_idx}")
            return
            
        source_path = Path(virtual_page.source_doc.name)
        source_idx = virtual_page.source_page_index
        
        log_debug(f"MainWindow: Resolvido highlight para física: {source_path.name} [pg {source_idx}]")

        # Guardar estado visual (scroll) para restaurar após reload
        scroll_v = self.viewer.verticalScrollBar().value() if self.viewer else 0

        try:
            from src.application.use_cases.add_annotation import AddAnnotationUseCase
            uc = AddAnnotationUseCase(self._adapter)
            
            # Adicionar anotação no arquivo físico
            new_path = uc.execute(source_path, source_idx, rect, color=color)
            
            if new_path and new_path.exists():
                self.statusBar().showMessage(f"Realce aplicado em {new_path.name}", 3000)
                
                # Sincronizar UI (Abrir o novo arquivo resultante)
                # O open_file cuidará de atualizar o TabContainer, StateManager e Viewers
                self.open_file(new_path)
                
                # Restaurar posição de leitura com ligeiro atraso para garantir render base
                QTimer.singleShot(600, lambda: self.viewer.verticalScrollBar().setValue(scroll_v) if self.viewer else None)

        except Exception as e:
            log_exception(f"MainWindow: Falha ao aplicar highlight: {e}")
            self.statusBar().showMessage(f"Erro ao salvar realce: {e}", 5000)

    def _navigate_to_physical_page(self, source_path: str, original_idx: int, highlights: list = None):
        """Converte um índice físico (do arquivo original) em índice visual (posição atual) e navega."""
        if not self.state_manager or not self.viewer:
            return
            
        visual_idx = self.state_manager.find_visual_index(source_path, original_idx)
        if visual_idx != -1:
            log_debug(f"Navegação: Físico {original_idx} -> Visual {visual_idx}")
            self.viewer.scroll_to_page(visual_idx, highlights=highlights)
        else:
            log_error(f"Navegação: Não foi possível encontrar a página física {original_idx} de {source_path}")
            self.statusBar().showMessage("Página não encontrada no documento atual.", 3000)

    def _undo_action(self):
        """Reverte para o estado anterior do documento atual."""
        if not self.tabs or not self.tabs.current_editor(): return
        
        group = self.tabs.current_editor()
        prev_state = group.action_stack.undo()
        
        if prev_state:
            log_debug(f"Undo: Revertendo para {prev_state.name}")
            scroll_pos = self.viewer.verticalScrollBar().value()
            
            group.load_document(prev_state, group.metadata, preserve_history=True)
            
            self.current_file = prev_state
            self.setWindowTitle(f"fotonPDF - {prev_state.name}")
            idx = self.tabs.currentIndex()
            if idx >= 0:
                self.tabs.setTabText(idx, prev_state.name)
                
            QTimer.singleShot(500, lambda: self.viewer.verticalScrollBar().setValue(scroll_pos))
            self.bottom_panel.add_log(f"↩️ Desfeito: {prev_state.name}")
        else:
            self.statusBar().showMessage("Nada para desfazer.")

    def _redo_action(self):
        """Refaz a última ação desfeita."""
        if not self.tabs or not self.tabs.current_editor(): return

        group = self.tabs.current_editor()
        next_state = group.action_stack.redo()
        
        if next_state:
            log_debug(f"Redo: Avançando para {next_state.name}")
            scroll_pos = self.viewer.verticalScrollBar().value()
            
            group.load_document(next_state, group.metadata, preserve_history=True)
            
            self.current_file = next_state
            self.setWindowTitle(f"fotonPDF - {next_state.name}")
            idx = self.tabs.currentIndex()
            if idx >= 0:
                self.tabs.setTabText(idx, next_state.name)
                
            QTimer.singleShot(500, lambda: self.viewer.verticalScrollBar().setValue(scroll_pos))
            self.bottom_panel.add_log(f"↪️ Refeito: {next_state.name}")
        else:
            self.statusBar().showMessage("Nada para refazer.")

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
