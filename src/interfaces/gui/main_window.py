import sys
from pathlib import Path
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QFileDialog, QStatusBar, QToolBar, QLabel)
from PyQt6.QtGui import QAction, QIcon, QDragEnterEvent, QDropEvent
from PyQt6.QtCore import Qt, QSize

from src.interfaces.gui.widgets.viewer_widget import PDFViewerWidget
from src.interfaces.gui.widgets.thumbnail_panel import ThumbnailPanel
from src.infrastructure.services.logger import log_debug, log_exception

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

        # Components
        self.sidebar = ThumbnailPanel()
        self.viewer = PDFViewerWidget()
        
        # Setup Layout
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.viewer, stretch=1)

        # UI Initialization
        self._setup_toolbar()
        self._setup_statusbar()
        self._setup_connections()
        
        # State
        self.current_file = None
        self.state_manager = None
        
        # Menu Contexto / Drag & Drop
        self.setAcceptDrops(True)
        self.sidebar.setAcceptDrops(True)
        # Custom drop for sidebar to handle APPEND
        self.sidebar.dragEnterEvent = self._on_sidebar_drag_enter
        self.sidebar.dropEvent = self._on_sidebar_drop

        # Placeholder
        self.viewer.setPlaceholder(QLabel("Arraste um PDF aqui para começar"))

        if initial_file:
            self.open_file(Path(initial_file))

    def _setup_toolbar(self):
        toolbar = QToolBar("Ferramentas")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)

        # Open
        open_action = QAction("Abrir", self)
        open_action.triggered.connect(self._on_open_clicked)
        toolbar.addAction(open_action)

        # Save
        self.save_action = QAction("Salvar", self)
        self.save_action.setEnabled(False)
        self.save_action.triggered.connect(self._on_save_clicked)
        toolbar.addAction(self.save_action)

        toolbar.addSeparator()

        # Merge
        merge_action = QAction("Unir PDF", self)
        merge_action.triggered.connect(self._on_merge_clicked)
        toolbar.addAction(merge_action)

        toolbar.addSeparator()

        # Rotation
        self.rotate_left_action = QAction("Gir -90°", self)
        self.rotate_left_action.setEnabled(False)
        self.rotate_left_action.triggered.connect(lambda: self._on_rotate_clicked(-90))
        toolbar.addAction(self.rotate_left_action)

        self.rotate_right_action = QAction("Gir +90°", self)
        self.rotate_right_action.setEnabled(False)
        self.rotate_right_action.triggered.connect(lambda: self._on_rotate_clicked(90))
        toolbar.addAction(self.rotate_right_action)

        toolbar.addSeparator()

        # Zoom
        zoom_in_action = QAction("Zoom +", self)
        zoom_in_action.triggered.connect(self.viewer.zoom_in)
        toolbar.addAction(zoom_in_action)

        zoom_out_action = QAction("Zoom -", self)
        zoom_out_action.triggered.connect(self.viewer.zoom_out)
        toolbar.addAction(zoom_out_action)

        fit_width_action = QAction("Largura", self)
        fit_width_action.triggered.connect(self.viewer.fit_width)
        toolbar.addAction(fit_width_action)

    def _setup_statusbar(self):
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Pronto")

    def _setup_connections(self):
        self.sidebar.pageSelected.connect(self.viewer.scroll_to_page)
        self.sidebar.orderChanged.connect(self._on_pages_reordered)

    def open_file(self, file_path: Path):
        try:
            self.current_file = file_path
            from src.interfaces.gui.state.pdf_state import PDFStateManager
            self.state_manager = PDFStateManager()
            self.state_manager.load_base_document(str(file_path))
            
            self.viewer.load_document(file_path)
            self.sidebar.load_thumbnails(str(file_path))
            
            self.setWindowTitle(f"fotonPDF - {file_path.name}")
            self.statusBar().showMessage(f"Arquivo carregado: {file_path.name}")
            self._enable_actions(True)
        except Exception as e:
            log_exception(f"MainWindow: Erro ao abrir: {e}")
            self.statusBar().showMessage(f"Erro: {e}")

    def _enable_actions(self, enabled: bool):
        self.save_action.setEnabled(enabled)
        self.rotate_left_action.setEnabled(enabled)
        self.rotate_right_action.setEnabled(enabled)

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
        selected_indices = self.sidebar.get_selected_pages() # UserRole IDs
        if not selected_indices:
            self.statusBar().showMessage("Selecione páginas na barra lateral para girar.")
            return

        for idx in selected_indices:
            self.state_manager.rotate_page(idx, degrees)
            page_state = self.state_manager.get_page(idx)
            # Precisamos encontrar QUAL widget do viewer corresponde ao ID absoluto 'idx'
            # Na verdade, a ordem visual do viewer está em self.viewer._pages
            # E o item na sidebar tem o UserRole=idx.
            # Vamos simplificar: forçar renderização da página que tem esse source index.
            self.viewer.refresh_page(idx, rotation=page_state.absolute_rotation)
        
        self.statusBar().showMessage(f"Giro de {degrees}° aplicado.")

    def _on_pages_reordered(self, new_order: list[int]):
        """Sincroniza viewer e state com a nova ordem da sidebar."""
        if self.state_manager:
            self.state_manager.reorder_pages(new_order)
            self.viewer.reorder_pages(new_order)

    def _on_save_clicked(self):
        save_path, _ = QFileDialog.getSaveFileName(self, "Salvar PDF Como", "", "Arquivos PDF (*.pdf)")
        if save_path:
            self.state_manager.save(save_path)
            self.statusBar().showMessage(f"Salvo em: {Path(save_path).name}")

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
