from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QFileDialog, QStatusBar, QToolBar, QLabel, QTabWidget)
from PyQt6.QtGui import QAction, QIcon, QDragEnterEvent, QDropEvent, QKeySequence
from PyQt6.QtCore import Qt, QSize

from src.interfaces.gui.widgets.viewer_widget import PDFViewerWidget
from src.interfaces.gui.widgets.thumbnail_panel import ThumbnailPanel
from src.interfaces.gui.widgets.search_panel import SearchPanel
from src.interfaces.gui.widgets.toc_panel import TOCPanel

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

        # Use Cases & Adapter
        self._adapter = PyMuPDFAdapter()
        self._search_use_case = SearchTextUseCase(self._adapter)
        self._get_toc_use_case = GetTOCUseCase(self._adapter)
        self._detect_ocr_use_case = DetectTextLayerUseCase(self._adapter)
        self._apply_ocr_use_case = ApplyOCRUseCase(self._adapter)
        self._ocr_area_use_case = OCRAreaExtractionUseCase(self._adapter)
        self._add_annot_use_case = AddAnnotationUseCase(self._adapter)

        # Components
        self.viewer = PDFViewerWidget()
        self.sidebar = ThumbnailPanel()
        self.toc_panel = TOCPanel(self._get_toc_use_case)
        self.search_panel = SearchPanel(self._search_use_case)

        # Sidebar with Tabs
        self.sidebar_tabs = QTabWidget()
        self.sidebar_tabs.setFixedWidth(300)
        self.sidebar_tabs.addTab(self.sidebar, "Miniaturas")
        self.sidebar_tabs.addTab(self.toc_panel, "Sumário")
        self.sidebar_tabs.addTab(self.search_panel, "Busca")
        
        # Setup Layout
        self.main_layout.addWidget(self.sidebar_tabs)
        
        container = QWidget()
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(0,0,0,0)
        vbox.setSpacing(0)
        
        # Banner OCR (Oculto por padrão)
        from PyQt6.QtWidgets import QFrame, QPushButton
        self.ocr_banner = QFrame()
        self.ocr_banner.setFixedHeight(40)
        self.ocr_banner.setStyleSheet("background-color: #34495e; border-bottom: 2px solid #2c3e50;")
        banner_layout = QHBoxLayout(self.ocr_banner)
        banner_layout.setContentsMargins(15, 0, 15, 0)
        
        self.banner_label = QLabel("Este documento parece ser digitalizado. Deseja aplicar OCR para torná-lo pesquisável?")
        self.banner_label.setStyleSheet("color: #ecf0f1; font-weight: bold;")
        
        self.btn_apply_ocr = QPushButton("Aplicar OCR")
        self.btn_apply_ocr.setStyleSheet("background-color: #27ae60; color: white; border: none; padding: 5px 15px; border-radius: 3px;")
        self.btn_apply_ocr.clicked.connect(self._on_apply_ocr_clicked)
        
        banner_layout.addWidget(self.banner_label)
        banner_layout.addStretch()
        banner_layout.addWidget(self.btn_apply_ocr)
        
        self.ocr_banner.hide()
        
        vbox.addWidget(self.ocr_banner)
        vbox.addWidget(self.viewer, stretch=1)
        
        self.main_layout.addWidget(container, stretch=1)

        # Apply Visual Identity
        self.setStyleSheet(get_main_stylesheet())
        self._setup_window_icon()

        # UI Initialization
        self._setup_toolbar()
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
        self.sidebar.setAcceptDrops(True)
        # Custom drop for sidebar to handle APPEND
        self.sidebar.dragEnterEvent = self._on_sidebar_drag_enter
        self.sidebar.dropEvent = self._on_sidebar_drop

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

    def _setup_toolbar(self):
        toolbar = QToolBar("Ferramentas")
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setMovable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.addToolBar(toolbar)

        # --- GRUPO: NAVEGAÇÃO ---
        toolbar.addWidget(QLabel("  🔍 "))
        
        zoom_in_action = QAction("Zoom +", self)
        zoom_in_action.triggered.connect(self.viewer.zoom_in)
        toolbar.addAction(zoom_in_action)

        zoom_out_action = QAction("Zoom -", self)
        zoom_out_action.triggered.connect(self.viewer.zoom_out)
        toolbar.addAction(zoom_out_action)

        real_size_action = QAction("100%", self)
        real_size_action.triggered.connect(self.viewer.real_size)
        toolbar.addAction(real_size_action)

        fit_width_action = QAction("Largura", self)
        fit_width_action.triggered.connect(self.viewer.fit_width)
        toolbar.addAction(fit_width_action)

        fit_height_action = QAction("Altura", self)
        fit_height_action.triggered.connect(self.viewer.fit_height)
        toolbar.addAction(fit_height_action)

        toolbar.addSeparator()

        self.back_action = QAction("⬅️ Voltar", self)
        self.back_action.setEnabled(False)
        self.back_action.triggered.connect(self._on_back_clicked)
        toolbar.addAction(self.back_action)

        self.forward_action = QAction("➡️ Avançar", self)
        self.forward_action.setEnabled(False)
        self.forward_action.triggered.connect(self._on_forward_clicked)
        toolbar.addAction(self.forward_action)

        toolbar.addSeparator()

        # --- GRUPO: EDIÇÃO ---
        toolbar.addWidget(QLabel("  📅 "))
        
        open_action = QAction("Abrir", self)
        open_action.triggered.connect(self._on_open_clicked)
        toolbar.addAction(open_action)

        self.save_action = QAction("Salvar", self)
        self.save_action.setEnabled(False)
        self.save_action.triggered.connect(self._on_save_clicked)
        toolbar.addAction(self.save_action)

        self.save_as_action = QAction("Salvar Como", self)
        self.save_as_action.setEnabled(False)
        self.save_as_action.triggered.connect(self._on_save_as_clicked)
        toolbar.addAction(self.save_as_action)

        merge_action = QAction("Unir PDF", self)
        merge_action.triggered.connect(self._on_merge_clicked)
        toolbar.addAction(merge_action)

        self.rotate_left_action = QAction("Girar -90°", self)
        self.rotate_left_action.setEnabled(False)
        self.rotate_left_action.triggered.connect(lambda: self._on_rotate_clicked(-90))
        toolbar.addAction(self.rotate_left_action)

        self.rotate_right_action = QAction("Girar +90°", self)
        self.rotate_right_action.setEnabled(False)
        self.rotate_right_action.triggered.connect(lambda: self._on_rotate_clicked(90))
        toolbar.addAction(self.rotate_right_action)

        self.extract_action = QAction("Extrair", self)
        self.extract_action.setEnabled(False)
        self.extract_action.triggered.connect(self._on_extract_clicked)
        toolbar.addAction(self.extract_action)

        toolbar.addSeparator()

        # --- GRUPO: CONVERSÃO ---
        toolbar.addWidget(QLabel("  🚀 "))
        
        from PyQt6.QtWidgets import QToolButton, QMenu
        
        # Export Image (Dropdown)
        export_img_btn = QToolButton()
        export_img_btn.setText("Exportar Imagem")
        export_img_menu = QMenu(self)
        export_img_menu.addAction("PNG (Alta Resolução)").triggered.connect(lambda: self._on_export_image_clicked("png"))
        export_img_menu.addAction("JPG (Compacto)").triggered.connect(lambda: self._on_export_image_clicked("jpg"))
        export_img_menu.addAction("WebP (Otimizado)").triggered.connect(lambda: self._on_export_image_clicked("webp"))
        
        export_img_btn.setMenu(export_img_menu)
        export_img_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        toolbar.addWidget(export_img_btn)

        export_svg_action = QAction("SVG", self)
        export_svg_action.triggered.connect(self._on_export_svg_clicked)
        toolbar.addAction(export_svg_action)

        export_md_action = QAction("Markdown", self)
        export_md_action.triggered.connect(self._on_export_md_clicked)
        toolbar.addAction(export_md_action)

        toolbar.addSeparator()

        # --- GRUPO: INTELIGÊNCIA OCR ---
        toolbar.addWidget(QLabel("  🧠 "))
        self.ocr_area_action.setEnabled(False)
        self.ocr_area_action.triggered.connect(self._on_ocr_area_toggled)
        toolbar.addAction(self.ocr_area_action)

        toolbar.addSeparator()

        # --- GRUPO: VISUALIZAÇÃO ---
        toolbar.addWidget(QLabel("  👁️ "))
        
        # Reading Modes (Dropdown)
        reading_mode_btn = QToolButton()
        reading_mode_btn.setText("Modo de Leitura")
        rm_menu = QMenu(self)
        rm_menu.addAction("Padrão").triggered.connect(lambda: self.viewer.set_reading_mode("default"))
        rm_menu.addAction("Sépia").triggered.connect(lambda: self.viewer.set_reading_mode("sepia"))
        rm_menu.addAction("Noturno").triggered.connect(lambda: self.viewer.set_reading_mode("dark"))
        rm_menu.addAction("Madrugada (Extra Dark)").triggered.connect(lambda: self.viewer.set_reading_mode("night"))
        
        reading_mode_btn.setMenu(rm_menu)
        reading_mode_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        toolbar.addWidget(reading_mode_btn)

        # Layout Mode (Dual View)
        self.layout_action = QAction("Lado a Lado", self)
        self.layout_action.setCheckable(True)
        self.layout_action.triggered.connect(self._on_layout_toggled)
        toolbar.addAction(self.layout_action)

        self.highlight_action = QAction("Realçar (Highlight)", self)
        self.highlight_action.setCheckable(True)
        self.highlight_action.triggered.connect(self._on_highlight_toggled)
        toolbar.addAction(self.highlight_action)

    def _setup_statusbar(self):
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Pronto")

    def _setup_connections(self):
        self.sidebar.pageSelected.connect(self.viewer.scroll_to_page)
        self.sidebar.orderChanged.connect(self._on_pages_reordered)
        
        # Novas conexões da Sprint 6
        self.viewer.pageChanged.connect(self._on_page_changed)
        self.search_panel.result_clicked.connect(self.viewer.scroll_to_page)
        self.toc_panel.bookmark_clicked.connect(self.viewer.scroll_to_page)
        
        # Atalhos
        self.search_shortcut = QAction("Search", self)
        self.search_shortcut.setShortcut(QKeySequence("Ctrl+F"))
        self.search_shortcut.triggered.connect(self._focus_search)
        self.addAction(self.search_shortcut)

        self.viewer.areaSelected.connect(self._on_area_selected)

    def open_file(self, file_path: Path):
        try:
            self.current_file = file_path
            from src.interfaces.gui.state.pdf_state import PDFStateManager
            self.state_manager = PDFStateManager()
            self.state_manager.load_base_document(str(file_path))
            
            self.viewer.load_document(file_path)
            self.sidebar.load_thumbnails(str(file_path))
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

    def _on_save_clicked(self):
        """Sobrescreve o arquivo atual."""
        if not self.state_manager or not self.current_file: return
        try:
            self.state_manager.save(str(self.current_file))
            self.statusBar().showMessage(f"Arquivo salvo: {self.current_file.name}")
        except Exception as e:
            self.statusBar().showMessage(f"Erro ao salvar: {e}")

    def _on_save_as_clicked(self):
        """Salva o estado atual em um novo local."""
        if not self.state_manager: return
        file_path, _ = QFileDialog.getSaveFileName(self, "Salvar PDF Como", "", "Arquivos PDF (*.pdf)")
        if file_path:
            self.state_manager.save(file_path)
            self.statusBar().showMessage(f"Salvo como: {Path(file_path).name}")

    def _on_extract_clicked(self):
        """Salva as páginas selecionadas em um novo arquivo."""
        if not self.state_manager: return
        selected_rows = self.sidebar.get_selected_rows()
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

    def _append_pdf(self, path: Path):
        """Implementação do Merge 2.0 (Incremental)."""
        if not self.state_manager:
            self.open_file(path)
            return

        try:
            self.state_manager.append_document(str(path))
            # Atualizar viewer e sidebar instantaneamente
            self.viewer.add_pages(path)
            self.sidebar.append_thumbnails(str(path))
            self.statusBar().showMessage(f"Anexado: {path.name}")
        except Exception as e:
            log_exception(f"MainWindow: Erro ao anexar: {e}")

    def _on_rotate_clicked(self, degrees: int):
        # Agora usamos as linhas VISUAIS
        selected_rows = self.sidebar.get_selected_rows()
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
        self.sidebar_tabs.setCurrentIndex(2) # Aba de Busca
        self.search_panel.search_input.setFocus()

    def _on_page_changed(self, index: int):
        """Chamado sempre que o viewer muda de página."""
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
