import fitz
from PyQt6.QtCore import QObject, QRunnable, QThreadPool, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QImage, QPixmap
from src.infrastructure.services.logger import log_debug, log_error, log_exception

class RenderTask(QRunnable):
    """Tarefa individual de renderização para o ThreadPool."""
    
    class Signals(QObject):
        finished = pyqtSignal(int, QPixmap, float, int) # index, pixmap, zoom, rotation

    def __init__(self, doc_path, page_num, zoom, rotation):
        super().__init__()
        self.doc_path = doc_path
        self.page_num = page_num
        self.zoom = zoom
        self.rotation = rotation
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
                
            pix = page.get_pixmap(matrix=mat, alpha=True)
            
            if not pix.samples:
                return
                
            fmt = QImage.Format.Format_RGBA8888
            img = QImage(pix.samples, pix.width, pix.height, pix.stride, fmt)
            
            if not img.isNull():
                pixmap = QPixmap.fromImage(img)
                self.signals.finished.emit(self.page_num, pixmap, self.zoom, self.rotation)
                
        except Exception as e:
            log_error(f"RenderTask: Erro na página {self.page_num}: {e}")
        finally:
            if doc:
                doc.close()

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

    def request_render(self, doc_path, page_num, zoom, rotation, callback):
        """Adiciona uma solicitação de renderização à fila."""
        task = RenderTask(doc_path, page_num, zoom, rotation)
        task.signals.finished.connect(callback)
        self.pool.start(task)

    def cancel_all(self):
        """Limpa a fila de tarefas pendentes."""
        self.pool.clear()
        log_debug("RenderEngine: Fila de renderização limpa.")
