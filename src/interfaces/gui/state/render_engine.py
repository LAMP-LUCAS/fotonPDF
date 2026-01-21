import fitz
from PyQt6.QtCore import QObject, QRunnable, QThreadPool, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QImage, QPixmap
from src.infrastructure.services.logger import log_debug, log_error, log_exception

class RenderTask(QRunnable):
    """Tarefa individual de renderização para o ThreadPool."""
    
    class Signals(QObject):
        finished = pyqtSignal(int, QPixmap, float, int, str) # index, pixmap, zoom, rotation, mode

    def __init__(self, doc_path, page_num, zoom, rotation, mode="default"):
        super().__init__()
        self.doc_path = doc_path
        self.page_num = page_num
        self.zoom = zoom
        self.rotation = rotation
        self.mode = mode
        self.signals = self.Signals()

    @pyqtSlot()
    def run(self):
        doc = None
        try:
            doc = fitz.open(self.doc_path)
            page = doc.load_page(self.page_num)
            
            mat = fitz.Matrix(self.zoom, self.zoom)
            if self.rotation != 0:
                mat.prerotate(self.rotation)
                
            pix = page.get_pixmap(matrix=mat, alpha=False) # Alpha False for better filter application
            
            if not pix.samples:
                return
                
            fmt = QImage.Format.Format_RGB888
            img = QImage(pix.samples, pix.width, pix.height, pix.stride, fmt).copy() # Copy to avoid buffer issues
            
            # Application of Reading Modes
            if self.mode == "dark":
                img.invertPixels()
            elif self.mode == "sepia":
                self._apply_sepia(img)
            elif self.mode == "night":
                img.invertPixels()
                # Additional darkening would go here if needed
                
            if not img.isNull():
                pixmap = QPixmap.fromImage(img)
                self.signals.finished.emit(self.page_num, pixmap, self.zoom, self.rotation, self.mode)
                
        except Exception as e:
            log_error(f"RenderTask: Erro na página {self.page_num}: {e}")
        finally:
            if doc:
                doc.close()

    def _apply_sepia(self, img: QImage):
        """Aplica filtro sépia diretamente nos pixels da QImage."""
        for y in range(img.height()):
            for x in range(img.width()):
                pixel = img.pixel(x, y)
                r = (pixel >> 16) & 0xff
                g = (pixel >> 8) & 0xff
                b = pixel & 0xff
                
                tr = min(255, int(0.393 * r + 0.769 * g + 0.189 * b))
                tg = min(255, int(0.349 * r + 0.686 * g + 0.168 * b))
                tb = min(255, int(0.272 * r + 0.534 * g + 0.131 * b))
                
                from PyQt6.QtGui import QColor
                img.setPixel(x, y, QColor(tr, tg, tb).rgb())

class RenderEngine(QObject):
    """Gerenciador central de renderização (Singleton)."""
    
    _instance = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        super().__init__()
        self.pool = QThreadPool()
        # Limitar a 2 threads simultâneas para máxima estabilidade no Windows
        self.pool.setMaxThreadCount(2)
        log_debug(f"RenderEngine: Iniciado com {self.pool.maxThreadCount()} threads.")

    def request_render(self, doc_path, page_num, zoom, rotation, callback, mode="default"):
        """Adiciona uma solicitação de renderização à fila."""
        task = RenderTask(doc_path, page_num, zoom, rotation, mode)
        task.signals.finished.connect(callback)
        self.pool.start(task)

    def cancel_all(self):
        """Limpa a fila de tarefas pendentes."""
        self.pool.clear()
        log_debug("RenderEngine: Fila de renderização limpa.")
