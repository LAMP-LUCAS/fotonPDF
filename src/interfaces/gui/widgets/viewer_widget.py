from pathlib import Path
import fitz
from PyQt6.QtWidgets import QScrollArea, QVBoxLayout, QWidget, QFrame
from PyQt6.QtCore import Qt
from src.interfaces.gui.widgets.page_widget import PageWidget

class PDFViewerWidget(QScrollArea):
    """Widget de visualização com suporte a Renderização Assíncrona."""

    def __init__(self):
        super().__init__()
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setStyleSheet("background-color: #1e1e1e;") # Darker theme
        
        self.container = QWidget()
        self.layout = QVBoxLayout(self.container)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.setSpacing(30)
        self.layout.setContentsMargins(40, 40, 40, 40)
        
        self.setWidget(self.container)
        self._doc = None
        self._placeholder = None
        self._pages = []

        # Connect scroll event for lazy rendering
        self.verticalScrollBar().valueChanged.connect(self.check_visibility)

    def has_document(self) -> bool:
        return self._doc is not None

    def setPlaceholder(self, widget: QWidget):
        if self._placeholder:
            self._placeholder.deleteLater()
        self._placeholder = widget
        self.layout.addWidget(widget)

    def load_document(self, path: Path):
        """Carrega o documento e prepara os placeholders das páginas."""
        if self._placeholder:
            self._placeholder.hide()
            
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        self._pages = []
        self._doc = fitz.open(str(path))
        
        for i in range(len(self._doc)):
            page_widget = PageWidget(i)
            self.layout.addWidget(page_widget)
            self._pages.append(page_widget)
        
        self.verticalScrollBar().setValue(0)
        self.check_visibility()
        return self._doc # Retorna para o ThumbnailPanel usar

    def scroll_to_page(self, page_num: int):
        """Scrolla o visualizador para uma página específica."""
        if 0 <= page_num < len(self._pages):
            page_widget = self._pages[page_num]
            self.verticalScrollBar().setValue(page_widget.pos().y())

    def check_visibility(self):
        """Ativa a renderização das páginas que entram no viewport."""
        if not self._doc:
            return
            
        viewport_top = self.verticalScrollBar().value()
        viewport_bottom = viewport_top + self.height()
        
        # Buffer de 1000 pixels acima e abaixo
        buffer = 1000 
        
        for page in self._pages:
            pos = page.pos().y()
            if pos < viewport_bottom + buffer and pos + page.height() > viewport_top - buffer:
                page.render_page(self._doc)

    def closeEvent(self, event):
        if self._doc:
            self._doc.close()
        super().closeEvent(event)
