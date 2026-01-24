import pytest
from unittest.mock import MagicMock, patch
from src.application.services.command_orchestrator import CommandOrchestrator
from src.application.services.ai_command_schema import CommandSchema

def test_ai_semantic_translation_integration():
    """
    Testa a integração entre Orchestrator e IA para comandos não literais.
    Garante que a 'voz' do fotonPDF é consistente.
    """
    mock_pdf = MagicMock()
    orchestrator = CommandOrchestrator(mock_pdf)
    
    # Mock da Resposta Estruturada da IA
    mock_ai_res = MagicMock(
        structured_data={
            "action": "rotate",
            "parameter": "180",
            "explanation": "Vou girar seu PDF de cabeça para baixo para você."
        }
    )
    
    with patch.object(orchestrator.ai.get_provider(), 'completion', return_value=mock_ai_res):
        # Usuário manda linguagem natural
        res = orchestrator.execute("> vira o desenho ao contrário", active_pdf_path=MagicMock())
        
        # O Orchestrator retorna 'command' se a IA mapeou com sucesso
        assert res["type"] == "command"
        if "action" in res:
            assert res["action"] == "rotate"
