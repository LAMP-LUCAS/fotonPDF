import fitz
from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt, QThread, pyqtSignal

class RenderWorker(QThread):
    finished = pyqtSignal(QPixmap)

    def __init__(self, doc, page_num, zoom=1.5):
        super().__init__()
        self.doc = doc
        self.page_num = page_num
        self.zoom = zoom

    def run(self):
        page = self.doc.load_page(self.page_num)
        pix = page.get_pixmap(matrix=fitz.Matrix(self.zoom, self.zoom))
        
        fmt = QImage.Format.Format_RGBA8888
        img = QImage(pix.samples, pix.width, pix.height, pix.stride, fmt)
        self.finished.emit(QPixmap.fromImage(img))

class PageWidget(QLabel):
    """Widget de página que renderiza sob demanda."""

    def __init__(self, page_num, parent=None):
        super().__init__(parent)
        self.page_num = page_num
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("background-color: white; border: 1px solid #111;")
        self.setMinimumHeight(400) # Placeholder height
        self._rendered = False

    def render_page(self, doc):
        if self._rendered:
            return
            
        self.worker = RenderWorker(doc, self.page_num)
        self.worker.finished.connect(self.on_render_finished)
        self.worker.start()

    def on_render_finished(self, pixmap):
        self.setPixmap(pixmap)
        self._rendered = True
        self.setMinimumHeight(0) # Reset placeholder height
