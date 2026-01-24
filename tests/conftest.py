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
