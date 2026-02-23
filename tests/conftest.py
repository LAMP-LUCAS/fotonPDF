import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from src.domain.entities.pdf import PDFDocument

@pytest.fixture
def mock_settings():
    """Fixture para mockar o SettingsService."""
    with patch('src.infrastructure.services.settings_service.SettingsService.instance') as mock:
        settings = MagicMock()
        settings.get.side_effect = lambda k, d=None: {
            "ai_provider": "ollama",
            "ai_model": "llama3",
            "language": "pt-BR"
        }.get(k, d)
        mock.return_value = settings
        yield settings

@pytest.fixture
def mock_pdf_ops():
    """Fixture para mockar o PDFOperationsPort."""
    return MagicMock()

@pytest.fixture
def sample_pdf_path(tmp_path):
    """Cria um arquivo PDF fake para testes."""
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_text("%PDF-1.4")
    return pdf_path

@pytest.fixture
def pdf_document(sample_pdf_path):
    """Fixture para a entidade PDFDocument."""
    return PDFDocument.from_path(sample_pdf_path)

@pytest.fixture
def mock_ai_provider():
    """Fixture para mockar um provedor de IA."""
    provider = MagicMock()
    provider.completion.return_value = MagicMock(
        text="Mocked AI Response",
        structured_data={"action": "none"},
        provider="mock"
    )
    return provider

@pytest.fixture(autouse=True)
def qt_teardown():
    """
    Global Teardown Fixture to resolve 'RuntimeError: wrapped C/C++ object has been deleted'.
    Forces event loop processing and threadpool cleanup after every test to ensure 
    dangling async tasks (QTimer.singleShot, QRunnable) complete or abort safely.
    Checks dynamically if a QApplication instance exists to avoid crashing non-UI unit tests.
    """
    yield
    from PyQt6.QtCore import QThreadPool
    from PyQt6.QtWidgets import QApplication
    from src.interfaces.gui.state.render_engine import RenderEngine
    
    app = QApplication.instance()
    
    # Process pending UI events if app exists
    if app:
        app.processEvents()
    
    # Safely clear the global ThreadPool
    QThreadPool.globalInstance().clear()
    
    # Safely shutdown the Render Engine (it owns a separate pool)
    engine = RenderEngine._instance
    if engine:
        try:
            engine.shutdown()
        except Exception:
            pass

    # A final pass for any timers that fired due to the shutdown
    if app:
        app.processEvents()
