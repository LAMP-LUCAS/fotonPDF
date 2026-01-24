import pytest
from unittest.mock import MagicMock, patch
from src.application.services.intelligence_core import IntelligenceCore
from src.infrastructure.services.ai_litellm_provider import LiteLLMProvider
from src.domain.services.ai_provider import AIResponse

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
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Hello World"))],
            provider="ollama"
        )
        
        response = provider.completion("Hi")
        assert response.text == "Hello World"
        assert response.provider == "ollama"

@pytest.mark.parametrize("query,expected_action", [
    ("> girar 90", "rotate"),
    ("> rotate left", "rotate"),
])
def test_orchestrator_literal_commands(query, expected_action):
    """Verifica se comandos literais são processados sem IA."""
    mock_pdf = MagicMock()
    from src.application.services.command_orchestrator import CommandOrchestrator
    orchestrator = CommandOrchestrator(mock_pdf)
    
    # Mock do resolve() do Path para evitar erros de sistema de arquivo
    with patch('pathlib.Path.resolve', return_value=MagicMock(exists=lambda: True)):
        res = orchestrator.execute(query, active_pdf_path=MagicMock())
        assert res["type"] == "command"
        assert res["action"] == expected_action
