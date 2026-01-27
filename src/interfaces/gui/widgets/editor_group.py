from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSplitter, QFrame, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
from src.interfaces.gui.widgets.viewer_widget import PDFViewerWidget
from src.interfaces.gui.utils.ui_error_boundary import safe_ui_callback, ResilientWidget

class EditorGroup(ResilientWidget):
    """
    Grupo de editores que suporta o 'Async Split' (mesmo documento, visões independentes).
    Fica dentro de uma Aba no TabContainer.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        # ResilientWidget já cria self.main_layout e self.content_layout
        self.layout = self.content_layout 
        
        # Banner OCR (Modular)
        self.ocr_banner = QFrame()
        self.ocr_banner.setFixedHeight(40)
        self.ocr_banner.setStyleSheet("background-color: #007acc; color: white; border-bottom: 1px solid #1e1e1e;")
        banner_layout = QHBoxLayout(self.ocr_banner)
        banner_layout.setContentsMargins(15, 0, 15, 0)
        
        self.ocr_label = QLabel("Este documento não possui camada de texto. Deseja aplicar OCR?")
        self.ocr_label.setStyleSheet("font-size: 11px; font-weight: bold;")
        
        self.btn_apply_ocr = QPushButton("Aplicar OCR")
        self.btn_apply_ocr.setFixedSize(100, 24)
        self.btn_apply_ocr.setStyleSheet("background: #094771; color: white; border: 1px solid #007acc; border-radius: 3px;")
        
        banner_layout.addWidget(self.ocr_label)
        banner_layout.addStretch()
        banner_layout.addWidget(self.btn_apply_ocr)
        self.ocr_banner.hide()
        
        self.layout.addWidget(self.ocr_banner)
        
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.layout.addWidget(self.splitter)
        
        # Primeiro visualizador (Sempre presente)
        self.viewer_left = PDFViewerWidget()
        self.splitter.addWidget(self.viewer_left)
        
        self.viewer_right = None
        self.current_file = None
        self.metadata = None

    @safe_ui_callback("Load Document")
    def load_document(self, file_path, metadata):
        """Carrega o documento no(s) visualizador(es)."""
        from src.infrastructure.services.logger import log_debug
        log_debug(f"EditorGroup: load_document chamado para {file_path.name} (page_count={metadata.get('page_count', 0)})")
        self.current_file = file_path
        self.metadata = metadata
        self.viewer_left.load_document(file_path, metadata)
        if self.viewer_right:
            self.viewer_right.load_document(file_path, metadata)

    @safe_ui_callback("Toggle Async Split")
    def toggle_split(self):
        """Ativa/Desativa o split assíncrono do mesmo documento."""
        if self.viewer_right is None:
            # Ativar Split (Duplicar visualização do mesmo arquivo)
            self.viewer_right = PDFViewerWidget()
            if self.current_file:
                self.viewer_right.load_document(self.current_file, self.metadata)
            
            self.splitter.addWidget(self.viewer_right)
        else:
            # Desativar Split
            self.viewer_right.deleteLater()
            self.viewer_right = None

    def get_viewer(self):
        """Retorna o visualizador principal (ou o focado futuramente)."""
        return self.viewer_left
