from PyQt6.QtCore import QObject, QRunnable, QThreadPool, pyqtSignal, pyqtSlot, QMutex, QMutexLocker
from PyQt6.QtGui import QImage, QPixmap
from src.infrastructure.services.logger import log_debug, log_error, log_exception
from src.domain.ports.pdf_operations import PDFOperationsPort
from pathlib import Path
import queue

class RenderTask(QRunnable):
    """Tarefa individual de renderização para o ThreadPool."""
    
    class Signals(QObject):
        # Usamos QImage pois é thread-safe para transporte; QPixmap é apenas UI.
        finished = pyqtSignal(int, QImage, float, int, str, object) # index, image, zoom, rotation, mode, clip

    def __init__(self, adapter: PDFOperationsPort, acquire_handle_cb, release_handle_cb, page_num, zoom, rotation, session_id, mode="default", clip=None):
        super().__init__()
        self._adapter = adapter
        self.acquire_handle = acquire_handle_cb
        self.release_handle = release_handle_cb
        self.page_num = page_num
        self.zoom = zoom
        self.rotation = rotation
        self.session_id = session_id
        self.mode = mode
        self.clip = clip # (x0, y0, x1, y1)
        self.signals = self.Signals()

    @pyqtSlot()
    def run(self):
        doc_handle = None
        try:
            current_zoom = self.zoom
            
            # Limite de segurança para evitar QImage gigantesca (> 5k)
            MAX_RES = 5120
            
            # OBTER HANDLE DO POOL (Single-Open Thread-Safe)
            doc_handle = self.acquire_handle(self.session_id)
            if not doc_handle:
                return
                
            if doc_handle.is_closed:
                raise ValueError("document closed")

            # Renderização via Adaptador REUSANDO O HANDLE
            samples, width, height, stride = self._adapter.render_page(
                None,  # Path é None pois passamos o handle
                self.page_num, 
                current_zoom, 
                self.rotation,
                clip=self.clip,
                doc_handle=doc_handle
            )
            
            # Se a imagem for muito grande, reduzir zoom e tentar novamente (Safety Pass)
            if (width > MAX_RES or height > MAX_RES) and self.clip is None:
                scale = MAX_RES / max(width, height)
                current_zoom *= scale
                log_debug(f"Render: Reduzindo zoom de segurança para {current_zoom:.2f} (Original: {self.zoom})")
                samples, width, height, stride = self._adapter.render_page(
                    None, self.page_num, current_zoom, self.rotation, doc_handle=doc_handle
                )

            if not samples:
                return
                
            fmt = QImage.Format.Format_RGB888
            # Criamos uma QImage que será enviada para a thread principal
            img = QImage(samples, width, height, stride, fmt).copy()
            
            # Filtros básicos agressivos
            if self.mode == "dark":
                img.invertPixels()
            elif self.mode == "sepia":
                self._apply_sepia(img)
            
            if not img.isNull():
                self.signals.finished.emit(self.page_num, img, self.zoom, self.rotation, self.mode, self.clip)
                
        except Exception as e:
            log_error(f"RenderTask Error [P{self.page_num}]: {e}")
        finally:
            if doc_handle:
                self.release_handle(doc_handle, self.session_id)

    def _apply_sepia(self, img: QImage):
        pass

class RenderEngine(QObject):
    """Gerenciador central de renderização com Single-Open Architecture."""
    
    _instance = None

    @classmethod
    def instance(cls, adapter: PDFOperationsPort = None):
        if cls._instance is None:
            cls._instance = cls(adapter=adapter)
        
        # Garantir re-inicialização se foi desligado p/ economia de recursos
        if not cls._instance._initialized:
            cls._instance._setup(adapter)
            
        return cls._instance

    def __init__(self, adapter: PDFOperationsPort = None):
        super().__init__()
        self._initialized = False
        self._setup(adapter)

    def _setup(self, adapter=None):
        if self._initialized: return
        
        # Injeção de dependência: se não provido, carregar o adapter padrão (Lazy)
        if adapter is None:
            from src.infrastructure.adapters.pymupdf_adapter import PyMuPDFAdapter
            self._adapter = PyMuPDFAdapter()
        else:
            self._adapter = adapter
            
        self.pool = QThreadPool()
        # Limitar a 2 threads para máxima estabilidade e evitar contenção na GUI Thread
        self.pool.setMaxThreadCount(2)
        
        # Cache de Pixmaps (Key: (path, page, zoom, rotation, mode, clip))
        self._cache = {}
        self._cache_order = []
        self._max_cache_size = 30 
        
        # Single-Open Management (Thread-Safe Pool)
        self._current_doc_path = None
        self._resolved_doc_path = None
        self._handle_queue = queue.Queue()
        self._created_handles_count = 0
        self._creation_mutex = QMutex()
        self._all_handles = [] # Keep track for closing
        self._current_session_id = 0
        self._path_resolver_cache = {} # Cache for Path.resolve()
        self._initialized = True
        
    @classmethod
    def reset_instance(cls):
        """Para uso em testes: força a criação de uma nova instância."""
        if cls._instance:
            try: cls._instance.shutdown()
            except: pass
        cls._instance = None

    def set_document(self, doc_path: Path, pre_opened_handle=None):
        """Define o documento ativo e inicia uma nova sessão."""
        if isinstance(doc_path, str):
            doc_path = Path(doc_path)

        # 1. Comparação robusta ANTES de qualquer ação
        if not pre_opened_handle and self._current_doc_path:
            try:
                # Otimização MM: Usar path resolvido em cache se disponível
                doc_path_resolved = self._resolve_path(doc_path)
                if self._resolved_doc_path and doc_path_resolved == self._resolved_doc_path:
                    return # Mesmo arquivo, ignorar skip
            except:
                if doc_path == self._current_doc_path:
                    return

        # 2. Se chegamos aqui, é um NOVO documento ou um Reload forçado
        log_debug(f"RenderEngine [S{self._current_session_id+1}]: Resetando motor para novo doc.")
        self.clear_queue()
        # REMOVIDO: self._close_all_handles() - Sessões agora cuidam do fechamento seguro
        
        # Incrementar Sessão
        with QMutexLocker(self._creation_mutex):
            self._current_session_id += 1
            sid = self._current_session_id
            
        self._current_doc_path = doc_path
        self._resolved_doc_path = self._resolve_path(doc_path)
            
        self._handle_queue = queue.Queue() # Fresh Queue
        self._all_handles = []
        self._created_handles_count = 0
        
        if pre_opened_handle:
            pre_opened_handle._session_id = sid
            self._handle_queue.put(pre_opened_handle)
            self._all_handles.append(pre_opened_handle)
            self._created_handles_count = 1
            log_debug(f"RenderEngine [S{sid}]: [STEP 1] Handle pré-aberto injetado.")
        
        log_debug(f"RenderEngine [S{sid}]: [STEP 2] Sessão inicializada.")

    def _close_all_handles(self):
        """Fecha todos os handles rastreados."""
        for handle in self._all_handles:
            try:
                handle.close()
            except: pass
        self._all_handles.clear()

    def _acquire_handle(self, request_session_id):
        """Adquire um handle da sessão solicitada. Descarta se for de sessão antiga."""
        import fitz
        
        while True:
            # 1. Tentar pegar da fila
            try:
                handle = self._handle_queue.get(timeout=0.1)
                
                # Validar Sessão
                handle_sid = getattr(handle, "_session_id", -1)
                if handle_sid != request_session_id or handle.is_closed:
                    log_debug(f"RenderEngine: Descartando handle de sessão antiga/fechado (H:S{handle_sid} != R:S{request_session_id})")
                    try: handle.close()
                    except: pass
                    with QMutexLocker(self._creation_mutex):
                        self._created_handles_count = max(0, self._created_handles_count - 1)
                    continue # Tentar próximo
                    
                return handle
            except queue.Empty:
                pass
            
            # 2. Se a sessão mudou enquanto esperávamos, falhar
            if request_session_id != self._current_session_id:
                return None

            # 3. Tentar criar novo se houver espaço
            should_create = False
            with QMutexLocker(self._creation_mutex):
                if self._created_handles_count < self.pool.maxThreadCount() and self._current_doc_path:
                    self._created_handles_count += 1
                    should_create = True
            
            if should_create:
                try:
                    log_debug(f"RenderEngine [S{request_session_id}]: Criando handle auxiliar ({self._created_handles_count})...")
                    new_handle = fitz.open(str(self._current_doc_path))
                    new_handle._session_id = request_session_id
                    
                    with QMutexLocker(self._creation_mutex):
                        self._all_handles.append(new_handle)
                    return new_handle
                except Exception as e:
                    log_error(f"RenderEngine: Falha ao criar handle: {e}")
                    with QMutexLocker(self._creation_mutex):
                        self._created_handles_count -= 1
                    return None

    def _release_handle(self, handle, session_id):
        """Devolve o handle ao pool ou fecha se for de sessão antiga."""
        if handle and not handle.is_closed and session_id == self._current_session_id:
            self._handle_queue.put(handle)
        else:
            log_debug(f"RenderEngine: Fechando handle de sessão expirada ou inválida (S{session_id})")
            try: handle.close()
            except: pass
            with QMutexLocker(self._creation_mutex):
                self._created_handles_count = max(0, self._created_handles_count - 1)

    def request_render(self, doc_path, page_num, zoom, rotation, callback, mode="default", clip=None, priority=0):
        """Adiciona uma solicitação de renderização."""
        if isinstance(doc_path, str):
            doc_path = Path(doc_path)
            
        # Comparação Robusta OTIMIZADA com cache de resolve()
        is_new = False
        if not self._current_doc_path:
            is_new = True
        else:
            try:
                # Compara strings se forem iguais, senão resolve (Custo-benefício)
                if doc_path != self._current_doc_path:
                    if self._resolve_path(doc_path) != self._resolved_doc_path:
                        is_new = True
            except:
                if doc_path != self._current_doc_path:
                    is_new = True

        if is_new:
            log_debug(f"RenderEngine: Request para novo doc {doc_path.name}. Resetando.")
            self.set_document(doc_path)

        cache_key = (doc_path, page_num, round(zoom, 3), rotation, mode, clip)
        
        if cache_key in self._cache:
            # Move to end (MRU)
            self._cache_order.remove(cache_key)
            self._cache_order.append(cache_key)
            pixmap = self._cache[cache_key]
            
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(0, lambda: callback(page_num, pixmap, zoom, rotation, mode, clip))
            return

        # Not in cache, start task
        task = RenderTask(
            self._adapter, 
            self._acquire_handle, 
            self._release_handle, 
            page_num, zoom, rotation,
            self._current_session_id,
            mode, clip
        )
        
        def on_finished(p_idx, img, z, r, m, c):
            if img.width() > 3000 or img.height() > 3000:
                log_debug(f"Render: Imagem pesada detectada ({img.width()}x{img.height()}).")
            
            pixmap = QPixmap.fromImage(img)
            self._update_cache(cache_key, pixmap)
            callback(p_idx, pixmap, z, r, m, c)
            
        task.signals.finished.connect(on_finished)
        self.pool.start(task, priority)

    def _update_cache(self, key, pixmap):
        if key in self._cache: return
            
        if len(self._cache) >= self._max_cache_size:
            del self._cache[self._cache_order.pop(0)]
            
        self._cache[key] = pixmap
        self._cache_order.append(key)

    def clear_queue(self):
        """Limpa a fila de tarefas pendentes e o cache."""
        self.pool.clear()
        self._cache.clear()
        self._cache_order.clear()
        # Não limpamos o _path_resolver_cache aqui para manter a performance 
        # entre trocas de abas rápidas.

    def _resolve_path(self, path: Path) -> Path:
        """Resolve o caminho de forma eficiente usando cache."""
        path_str = str(path)
        if path_str in self._path_resolver_cache:
            return self._path_resolver_cache[path_str]
        
        try:
            resolved = path.resolve()
            self._path_resolver_cache[path_str] = resolved
            return resolved
        except:
            return path

    def shutdown(self):
        """Encerra o pool e fecha todos os handles de forma definitiva."""
        if not hasattr(self, "pool") or self.pool is None: return
        
        try:
            log_debug("RenderEngine: Encerrando motor de renderização...")
            self.pool.waitForDone()
            self._close_all_handles()
            log_debug("RenderEngine: Motor encerrado com sucesso.")
        except:
             pass
        finally:
             self.pool = None
             self._initialized = False
