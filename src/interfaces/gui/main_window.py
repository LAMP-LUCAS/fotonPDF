import sys
from pathlib import Path
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QFileDialog, QLabel
from PyQt6.QtCore import Qt
from src.interfaces.gui.widgets.viewer_widget import PDFViewerWidget
from src.interfaces.gui.widgets.thumbnail_panel import ThumbnailPanel

class MainWindow(QMainWindow):
    """Janela Principal do fotonPDF."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("fotonPDF - Visualizador Ultra-Rápido")
        self.resize(1200, 900)
        
        # Central Widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Main Horizontal Layout
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = ThumbnailPanel()
        self.sidebar.pageSelected.connect(self.on_page_selected)
        self.main_layout.addWidget(self.sidebar)
        
        # Viewer
        self.viewer = PDFViewerWidget()
        self.main_layout.addWidget(self.viewer)
        
        # Drag & Drop support
        self.setAcceptDrops(True)
        
        # Placeholder se nenhum arquivo aberto
        self.show_welcome_message()
        
        # Carregar arquivo se passado via sys.argv
        if len(sys.argv) > 1:
            potential_file = Path(sys.argv[1])
            if potential_file.exists() and potential_file.suffix.lower() == ".pdf":
                self.open_file(potential_file)

    def show_welcome_message(self):
        if not self.viewer.has_document():
            label = QLabel("Arraste um PDF aqui para começar 🚀")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("font-size: 18px; color: #666; font-family: 'Segoe UI', sans-serif;")
            self.viewer.setPlaceholder(label)

    def open_file(self, file_path: Path):
        """Abre um novo arquivo PDF no visualizador e atualiza as miniaturas."""
        try:
            doc = self.viewer.load_document(file_path)
            self.sidebar.load_thumbnails(doc)
            self.setWindowTitle(f"fotonPDF - {file_path.name}")
        except Exception as e:
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
