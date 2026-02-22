import pytest
import time
from pathlib import Path
from src.interfaces.gui.state.render_engine import RenderEngine
from src.infrastructure.adapters.pymupdf_adapter import PyMuPDFAdapter

class MockCallback:
    def __init__(self):
        self.called = False
        self.results = []

    def __call__(self, page_index, pixmap, zoom, rotation, mode, clip):
        self.called = True
        self.results.append((page_index, pixmap.width(), pixmap.height()))

@pytest.fixture
def engine():
    adapter = PyMuPDFAdapter()
    engine = RenderEngine.instance(adapter=adapter)
    return engine

def test_render_concurrency_stress(engine):
    """Teste de estresse: solicita múltiplas renderizações rápidas para garantir que não há deadlock."""
    # Usar um arquivo de teste real se possível, ou um mock robusto.
    # Como estamos em ambiente real, vamos tentar abrir um PDF se existir.
    test_pdf = Path("docs/reports/Ideas/Visualizador PDF_ UI_UX Inspirada em VS Code, Obsidian, Cursor.pdf")
    if not test_pdf.exists():
        pytest.skip("Test PDF not found")

    callback = MockCallback()
    
    # Simular 20 requisições simultâneas (o pool tem 2 threads)
    for i in range(20):
        engine.request_render(test_pdf, 0, 1.0, 0, callback)
    
    # Aguardar processamento
    timeout = 10
    start = time.time()
    while len(callback.results) < 20 and (time.time() - start) < timeout:
        time.sleep(0.1)
    
    assert len(callback.results) == 20
    assert callback.called

def test_path_resolution_caching(engine):
    """Verifica se o cache de resolução de caminhos está funcionando."""
    test_pdf = Path("src/interfaces/gui/main_window.py") # Not a PDF, but Path.resolve() works
    
    start_time = time.time()
    for _ in range(100):
        engine._resolve_path(test_pdf)
    end_time = time.time()
    
    # O primeiro resolve() é real, os outros 99 são cache. 
    # Deve ser extremamente rápido (< 1ms no total teoricamente, mas vamos ser generosos)
    duration = end_time - start_time
    print(f"Path resolution duration for 100 calls: {duration:.6f}s")
    assert duration < 0.1 # 100ms é muito para cache, mas seguro para CI lento
