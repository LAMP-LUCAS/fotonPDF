import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock

class MockQObject:
    def __init__(self, *args, **kwargs): pass
    def setMaxThreadCount(self, *args, **kwargs): pass
    def maxThreadCount(self): return 2
    def start(self, *args, **kwargs): pass
    def clear(self, *args, **kwargs): pass
    def connect(self, *args, **kwargs): pass

class MockQTimer:
    @staticmethod
    def singleShot(ms, callback): callback()

class MockQtCore:
    QObject = MockQObject
    QRunnable = MockQObject
    QThreadPool = MockQObject
    pyqtSignal = MagicMock
    pyqtSlot = MagicMock
    QTimer = MockQTimer
    @staticmethod
    def singleShot(ms, callback): callback()
    def __getattr__(self, name): return MagicMock()

sys.modules['PyQt6.QtCore'] = MockQtCore
sys.modules['PyQt6.QtGui'] = MagicMock()
sys.modules['PyQt6.QtWidgets'] = MagicMock()

from src.interfaces.gui.state.render_engine import RenderEngine

class QPixmap:
    def __init__(self, *args): pass

class TestPerformance(unittest.TestCase):
    def test_render_engine_caching(self):
        """Valida que o cache LRU do RenderEngine funciona."""
        # Reset singleton to avoid interference from other tests
        RenderEngine._instance = None
        
        # Use MagicMock for Pixmap
        mock_pixmap = MagicMock()
        
        engine = RenderEngine.instance()
        engine.clear_queue()
        
        key = ("dummy.pdf", 0, 1.0, 0, "default")
        
        # Setup initial cache
        engine._update_cache(key, mock_pixmap)
        self.assertIn(key, engine._cache)
        
        # Test Retrieval
        callback_called = [False]
        def mock_callback(p, pix, z, r, m):
            callback_called[0] = True
            
        engine.request_render("dummy.pdf", 0, 1.0, 0, mock_callback)
        self.assertTrue(callback_called[0], "O callback deveria ter sido chamado via cache")

    def test_cache_eviction(self):
        """Valida a expulsão LRU quando o cache atinge o limite."""
        engine = RenderEngine.instance()
        engine.clear_queue()
        engine._max_cache_size = 2
        
        pix = QPixmap(1, 1)
        engine._update_cache("key1", pix)
        engine._update_cache("key2", pix)
        engine._update_cache("key3", pix) # Deve expulsar key1
        
        self.assertNotIn("key1", engine._cache)
        self.assertIn("key2", engine._cache)
        self.assertIn("key3", engine._cache)

if __name__ == '__main__':
    unittest.main()
