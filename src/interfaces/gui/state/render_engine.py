from PyQt6.QtCore import QObject, QRunnable, QThreadPool, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QImage, QPixmap
from src.infrastructure.services.logger import log_debug, log_error, log_exception
from src.infrastructure.adapters.pymupdf_adapter import PyMuPDFAdapter
from pathlib import Path

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
        self._adapter = PyMuPDFAdapter()

    @pyqtSlot()
    def run(self):
        try:
            # Uso da Porta através do Adaptador (Arquitetura Hexagonal)
            samples, width, height, stride = self._adapter.render_page(
                Path(self.doc_path), 
                self.page_num, 
                self.zoom, 
                self.rotation
            )
            
            if not samples:
                return
                
            fmt = QImage.Format.Format_RGB888
            img = QImage(samples, width, height, stride, fmt).copy() # Cópia para evitar problemas de buffer
            
            # Aplicação de Filtros (Contexto de Interface)
            if self.mode == "dark":
                img.invertPixels()
            elif self.mode == "sepia":
                self._apply_sepia(img)
            elif self.mode == "night":
                img.invertPixels()
            
            if not img.isNull():
                pixmap = QPixmap.fromImage(img)
                self.signals.finished.emit(self.page_num, pixmap, self.zoom, self.rotation, self.mode)
                
        except Exception as e:
            log_error(f"RenderTask: Erro na página {self.page_num}: {e}")

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
    """Gerenciador central de renderização com Cache LRU para performance extrema."""
    
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
        
        # Cache de Pixmaps (Key: (path, page, zoom, rotation, mode))
        self._cache = {}
        self._cache_order = []
        self._max_cache_size = 50 
        
        log_debug(f"RenderEngine: Iniciado com {self.pool.maxThreadCount()} threads e Cache LRU.")

    def request_render(self, doc_path, page_num, zoom, rotation, callback, mode="default"):
        """Adiciona uma solicitação de renderização ou retorna do cache."""
        cache_key = (doc_path, page_num, round(zoom, 3), rotation, mode)
        
        # Check Cache
        if cache_key in self._cache:
            # Move to end (MRU)
            self._cache_order.remove(cache_key)
            self._cache_order.append(cache_key)
            pixmap = self._cache[cache_key]
            # Emitir callback simulado (no próximo event loop para manter consistência)
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(0, lambda: callback(page_num, pixmap, zoom, rotation, mode))
            return

        # Not in cache, start task
        task = RenderTask(doc_path, page_num, zoom, rotation, mode)
        
        def on_finished(p_idx, pix, z, r, m):
            self._update_cache(cache_key, pix)
            callback(p_idx, pix, z, r, m)
            
        task.signals.finished.connect(on_finished)
        self.pool.start(task)

    def _update_cache(self, key, pixmap):
        if key in self._cache:
            return
            
        if len(self._cache) >= self._max_cache_size:
            oldest = self._cache_order.pop(0)
            del self._cache[oldest]
            
        self._cache[key] = pixmap
        self._cache_order.append(key)

    def clear_queue(self):
        """Limpa a fila de tarefas pendentes e o cache."""
        self.pool.clear()
        self._cache.clear()
        self._cache_order.clear()
        log_debug("RenderEngine: Fila e Cache limpos.")
