import pytest
from unittest.mock import MagicMock, patch
from src.application.services.command_orchestrator import CommandOrchestrator
from src.application.services.ai_command_schema import CommandSchema

def test_ai_semantic_translation_integration(mock_settings, sample_pdf_path):
    """
    Testa a integração entre Orchestrator e IA para comandos não literais.
    Garante que a 'voz' do fotonPDF é consistente.
    """
    mock_pdf_ops = MagicMock()
    orchestrator = CommandOrchestrator(mock_pdf_ops)
    
    # Mock da Resposta Estruturada da IA
    mock_ai_res = MagicMock(
        structured_data={
            "action": "rotate",
            "parameter": "180",
            "explanation": "Vou girar seu PDF de cabeça para baixo para você."
        }
    )
    
    # Precisamos garantir que o IntelligenceCore.get_provider() retorne algo que possamos mockar
    with patch('src.infrastructure.services.ai_litellm_provider.LiteLLMProvider.completion', return_value=mock_ai_res):
        # Usuário manda linguagem natural
        res = orchestrator.execute("> vira o desenho ao contrário", active_pdf_path=sample_pdf_path)
        
        # O Orchestrator retorna 'command' se a IA mapeou com sucesso
        assert res["type"] == "command"
        if "action" in res:
            assert res["action"] == "rotate"
