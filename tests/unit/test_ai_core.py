import pytest
from unittest.mock import MagicMock, patch
from src.application.services.intelligence_core import IntelligenceCore
from src.infrastructure.services.ai_litellm_provider import LiteLLMProvider
from src.domain.services.ai_provider import AIResponse
from src.domain.entities.pdf import PDFDocument

def test_intelligence_core_initialization():
    """Valida se o IntelligenceCore carrega os provedores corretamente."""
    with patch('src.infrastructure.services.settings_service.SettingsService.instance') as mock_settings:
        mock_settings.return_value.get.side_effect = lambda k, d=None: {
            "ai_provider": "ollama",
            "ai_model": "llama3"
        }.get(k, d)
        
        core = IntelligenceCore()
        provider = core.get_provider()
        assert isinstance(provider, LiteLLMProvider)
        assert provider.model == "ollama/llama3"

def test_litellm_provider_completion():
    """Valida se o provedor LiteLLM chama o motor corretamente."""
    provider = LiteLLMProvider("ollama/llama3", base_url="http://localhost:11434")
    
    with patch('litellm.completion') as mock_completion:
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Hello World"))]
        mock_response.get.side_effect = lambda k, d=None: {
            "provider": "ollama",
            "usage": {"total_tokens": 10}
        }.get(k, d)
        mock_completion.return_value = mock_response
        
        response = provider.completion("Hi")
        assert response.text == "Hello World"
        assert response.provider == "ollama"

@pytest.mark.parametrize("query,expected_action", [
    ("> girar 90", "rotate"),
    ("> rotate left", "rotate"),
])
def test_orchestrator_literal_commands(query, expected_action, sample_pdf_path):
    """Verifica se comandos literais são processados sem IA."""
    mock_pdf_ops = MagicMock()
    # Mock do get_info para retornar um PDFDocument válido
    mock_pdf_ops.get_info.return_value = PDFDocument(sample_pdf_path, "test.pdf")
    # Mock do rotate para retornar o path
    mock_pdf_ops.rotate.return_value = sample_pdf_path
    
    from src.application.services.command_orchestrator import CommandOrchestrator
    orchestrator = CommandOrchestrator(mock_pdf_ops)
    
    res = orchestrator.execute(query, active_pdf_path=sample_pdf_path)
    assert res["type"] == "command"
    assert res["action"] == expected_action
