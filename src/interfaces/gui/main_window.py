import sys
from pathlib import Path
from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
                             QFileDialog, QLabel, QToolBar, QStatusBar)
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt, QSize
from src.interfaces.gui.widgets.viewer_widget import PDFViewerWidget
from src.interfaces.gui.widgets.thumbnail_panel import ThumbnailPanel

from src.infrastructure.services.update_service import UpdateService

class MainWindow(QMainWindow):
    """Janela Principal do fotonPDF com Design Premium."""

    def __init__(self, initial_file: Path = None):
        super().__init__()
        self.setWindowTitle("fotonPDF")
        self.resize(1200, 900)
        self.current_file = None
        
        # Iniciar Verificador de Update
        self.update_service = UpdateService()
        self.update_service.check_for_updates(self._on_update_found)
        
        # Apply Premium Dark Theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121212;
            }
            QToolBar {
                background-color: #1e1e1e;
                border-bottom: 1px solid #333;
                padding: 10px;
                spacing: 15px;
            }
            QStatusBar {
                background-color: #1e1e1e;
                color: #888;
                border-top: 1px solid #333;
            }
            QLabel {
                color: #e0e0e0;
            }
        """)
        
        # Central Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Root Layout
        self.root_layout = QVBoxLayout(self.central_widget)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(0)
        
        # Toolbar
        self.toolbar = QToolBar("Ferramentas")
        self.toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(self.toolbar)
        self._setup_toolbar()
        
        # Content Layout
        self.content_layout = QHBoxLayout()
        self.content_layout.setSpacing(0)
        self.root_layout.addLayout(self.content_layout)
        
        # Sidebar
        self.sidebar = ThumbnailPanel()
        self.sidebar.pageSelected.connect(self.on_page_selected)
        self.content_layout.addWidget(self.sidebar)
        
        # Viewer
        self.viewer = PDFViewerWidget()
        self.content_layout.addWidget(self.viewer)
        
        # Status Bar
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Pronto")
        
        # Drag & Drop support
        self.setAcceptDrops(True)
        
        # Placeholder se nenhum arquivo aberto
        self.show_welcome_message()
        
        # Carregar arquivo se fornecido
        if initial_file:
            if initial_file.exists() and initial_file.suffix.lower() == ".pdf":
                self.open_file(initial_file)

    def show_welcome_message(self):
        if not self.viewer.has_document():
            label = QLabel("Arraste um PDF aqui para começar 🚀")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("font-size: 18px; color: #666; font-family: 'Segoe UI', sans-serif;")
            self.viewer.setPlaceholder(label)

    def _setup_toolbar(self):
        """Configura os botões da barra de ferramentas."""
        # Abrir
        open_action = QAction("Abrir", self)
        open_action.triggered.connect(self._on_open_clicked)
        self.toolbar.addAction(open_action)
        
        self.toolbar.addSeparator()
        
        # Extrair Páginas
        self.extract_action = QAction("Extrair Selecionadas", self)
        self.extract_action.setEnabled(False)
        self.extract_action.triggered.connect(self._on_extract_clicked)
        self.toolbar.addAction(self.extract_action)
        
        # Exportar Imagem
        self.export_action = QAction("Exportar como Imagem", self)
        self.export_action.setEnabled(False)
        self.export_action.triggered.connect(self._on_export_clicked)
        self.toolbar.addAction(self.export_action)

    def _on_open_clicked(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Abrir PDF", "", "Arquivos PDF (*.pdf)")
        if file_path:
            self.open_file(Path(file_path))

    def _on_extract_clicked(self):
        selected_pages = self.sidebar.get_selected_pages()
        if not selected_pages:
            self.statusBar().showMessage("Selecione ao menos uma página na barra lateral.")
            return

        save_path, _ = QFileDialog.getSaveFileName(self, "Salvar Extração", "", "Arquivos PDF (*.pdf)")
        if not save_path:
            return

        try:
            from src.application.use_cases.split_pdf import SplitPDFUseCase
            from src.infrastructure.adapters.pymupdf_adapter import PyMuPDFAdapter
            
            adapter = PyMuPDFAdapter()
            use_case = SplitPDFUseCase(adapter)
            
            use_case.execute(self.current_file, selected_pages, Path(save_path))
            self.statusBar().showMessage(f"Sucesso! {len(selected_pages)} páginas extraídas.")
        except Exception as e:
            self.statusBar().showMessage(f"Erro na extração: {str(e)}")

    def _on_export_clicked(self):
        selected_pages = self.sidebar.get_selected_pages()
        if not selected_pages:
            self.statusBar().showMessage("Selecione ao menos uma página na barra lateral.")
            return

        target_dir = QFileDialog.getExistingDirectory(self, "Selecionar Pasta para Exportação")
        if not target_dir:
            return

        try:
            import fitz
            doc = fitz.open(str(self.current_file))
            for page_num in selected_pages:
                page = doc.load_page(page_num - 1)
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2)) # Alta qualidade
                output_name = f"{self.current_file.stem}_page_{page_num}.png"
                pix.save(str(Path(target_dir) / output_name))
            
            doc.close()
            self.statusBar().showMessage(f"Exportação concluída em: {target_dir}")
        except Exception as e:
            self.statusBar().showMessage(f"Erro na exportação: {str(e)}")

    def _on_update_found(self, version, url):
        """Notifica o usuário sobre a nova versão."""
        from PyQt6.QtWidgets import QMessageBox
        msg = QMessageBox(self)
        msg.setWindowTitle("Atualização Disponível")
        msg.setText(f"Uma nova versão do fotonPDF (v{version}) está disponível!")
        msg.setInformativeText("Deseja baixar a atualização agora?")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setDefaultButton(QMessageBox.StandardButton.Yes)
        
        if msg.exec() == QMessageBox.StandardButton.Yes:
            import webbrowser
            webbrowser.open(url)

    def open_file(self, file_path: Path):
        """Abre um novo arquivo PDF no visualizador e atualiza as miniaturas."""
        try:
            self.current_file = file_path
            doc = self.viewer.load_document(file_path)
            self.sidebar.load_thumbnails(doc)
            self.setWindowTitle(f"fotonPDF - {file_path.name}")
            self.statusBar().showMessage(f"Arquivo carregado: {file_path.name}")
            self.extract_action.setEnabled(True)
            self.export_action.setEnabled(True)
        except Exception as e:
            self.statusBar().showMessage(f"Erro ao abrir arquivo: {str(e)}")
            print(f"Erro ao abrir PDF: {e}")

    def on_page_selected(self, page_num: int):
        self.viewer.scroll_to_page(page_num)

    def keyPressEvent(self, event):
        """Atalhos de teclado senior."""
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        elif event.key() == Qt.Key.Key_J: # Estilo Vim (Baixo)
            self.viewer.verticalScrollBar().setValue(self.viewer.verticalScrollBar().value() + 50)
        elif event.key() == Qt.Key.Key_K: # Estilo Vim (Cima)
            self.viewer.verticalScrollBar().setValue(self.viewer.verticalScrollBar().value() - 50)
        else:
            super().keyPressEvent(event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        files = [Path(u.toLocalFile()) for u in event.mimeData().urls()]
        if files and files[0].suffix.lower() == ".pdf":
            self.open_file(files[0])
