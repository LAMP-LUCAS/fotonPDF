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

from src.infrastructure.services.logger import log_debug, log_exception
from src.interfaces.gui.styles import get_main_stylesheet
from src.infrastructure.services.resource_service import ResourceService

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
        self.main_layout.addWidget(self.viewer, stretch=1)

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

        if initial_file:
            self.open_file(Path(initial_file))

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

    def open_file(self, file_path: Path):
        try:
            self.current_file = file_path
            from src.interfaces.gui.state.pdf_state import PDFStateManager
            self.state_manager = PDFStateManager()
            self.state_manager.load_base_document(str(file_path))
            
            self.viewer.load_document(file_path)
            self.sidebar.load_thumbnails(str(file_path))
            
            # Inicializar painéis da Sprint 6
            self.toc_panel.set_pdf(file_path)
            self.search_panel.set_pdf(file_path)
            
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
