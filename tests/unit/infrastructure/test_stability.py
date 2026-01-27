import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
from src.interfaces.gui.state.render_engine import RenderEngine
from src.domain.ports.pdf_operations import PDFOperationsPort

class MockSignal:
    def connect(self, *args, **kwargs): pass
    def emit(self, *args, **kwargs): pass

class MockQObject:
    def __init__(self, *args, **kwargs): 
        self.finished = MockSignal()
    def setMaxThreadCount(self, *args, **kwargs): pass
    def maxThreadCount(self): return 2
    def start(self, *args, **kwargs): pass
    def clear(self, *args, **kwargs): pass
    def connect(self, *args, **kwargs): pass

class MockQTimer:
    @staticmethod
    def singleShot(ms, callback): callback()

class MockQtCore:
    Qt = MagicMock()
    QObject = MockQObject
    QRunnable = MockQObject
    QThreadPool = MockQObject
    pyqtSignal = lambda *args: MockSignal()
    pyqtSlot = lambda *args: lambda x: x
    QTimer = MockQTimer
    @staticmethod
    def singleShot(ms, callback): callback()
    def __getattr__(self, name): return MagicMock()

# We need sys for the module patching
import sys

class TestPerformance(unittest.TestCase):
    def setUp(self):
        # We MUST ensure RenderEngine is NOT in sys.modules from previous tests
        # to force it to be re-imported under the mocks.
        for mod in list(sys.modules.keys()):
            if 'render_engine' in mod:
                del sys.modules[mod]
        RenderEngine._instance = None

    def test_render_engine_caching(self):
        """Valida que o cache LRU do RenderEngine funciona."""
        # Mocking sys.modules locally for this test
        # We MUST ensure RenderEngine is NOT in sys.modules from previous tests
        if 'src.interfaces.gui.state.render_engine' in sys.modules:
            del sys.modules['src.interfaces.gui.state.render_engine']

        with patch.dict('sys.modules', {
            'PyQt6.QtCore': MockQtCore,
            'PyQt6.QtGui': MagicMock(),
            'PyQt6.QtWidgets': MagicMock()
        }):
            from src.interfaces.gui.state.render_engine import RenderEngine
            RenderEngine._instance = None
            
            mock_pixmap = MagicMock()
            mock_adapter = MagicMock()
            
            engine = RenderEngine.instance(adapter=mock_adapter)
            engine.set_document(Path("dummy.pdf"))
            engine.clear_queue() # Just to be sure it's fresh after set_document
            # But set_document clears the queue anyway. Wait.
            # Actually set_document sets self._current_doc_path and clears cache.
            # So we MUST update cache AFTER set_document.
            
            # Key now includes 'clip' (None)
            key = (Path("dummy.pdf"), 0, 1.0, 0, "default", None)
            
            # Setup initial cache
            engine._update_cache(key, mock_pixmap)
            
            # Test Retrieval
            callback_called = [False]
            def mock_callback(p, pix, z, r, m, c):
                callback_called[0] = True
            
            engine.request_render(Path("dummy.pdf"), 0, 1.0, 0, mock_callback)
            
            # Como MockQTimer chama o callback sincronamente no nosso mock,
            # callback_called[0] deve ser True agora.
            self.assertTrue(callback_called[0], "O callback deveria ter sido chamado via cache")

    def test_cache_eviction(self):
        """Valida a expulsão LRU quando o cache atinge o limite."""
        if 'src.interfaces.gui.state.render_engine' in sys.modules:
            del sys.modules['src.interfaces.gui.state.render_engine']

        with patch.dict('sys.modules', {
            'PyQt6.QtCore': MockQtCore,
            'PyQt6.QtGui': MagicMock(),
            'PyQt6.QtWidgets': MagicMock()
        }):
            from src.interfaces.gui.state.render_engine import RenderEngine
            RenderEngine._instance = None
            
            engine = RenderEngine.instance()
            engine._max_cache_size = 2
            
            pix = MagicMock()
            engine._update_cache("key1", pix)
            engine._update_cache("key2", pix)
            engine._update_cache("key3", pix) # Deve expulsar key1
            
            self.assertNotIn("key1", engine._cache)
            self.assertIn("key2", engine._cache)
            self.assertIn("key3", engine._cache)

if __name__ == '__main__':
    unittest.main()
