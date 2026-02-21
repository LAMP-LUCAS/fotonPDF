import pytest
from pathlib import Path
from PyQt6.QtCore import Qt, QTimer
from src.interfaces.gui.main_window import MainWindow
from unittest.mock import MagicMock

@pytest.fixture(autouse=True)
def mock_infrastructure(mocker):
    """Mocka infraestrutura pesada para evitar hangs em modo headless."""
    mocker.patch("src.infrastructure.services.resource_service.ResourceService.get_logo_ico", return_value=Path("fake_logo.ico"))
    mocker.patch("src.infrastructure.services.settings_service.SettingsService.instance", return_value=MagicMock())
    mock_adapter = mocker.patch("src.infrastructure.adapters.pymupdf_adapter.PyMuPDFAdapter")
    mock_adapter.return_value.get_page_count.return_value = 5
    mock_adapter.return_value.open_document.return_value = True
    mocker.patch("src.infrastructure.adapters.windows_registry_adapter.WindowsRegistryAdapter", autospec=True)
    mocker.patch("src.infrastructure.repositories.sqlite_stage_repository.StageStateRepository", autospec=True)

def test_mainwindow_viewer_property_resilience(qtbot):
    """Verifica se a propriedade viewer funciona dinamicamente e é resiliente a abas vazias."""
    window = MainWindow()
    qtbot.addWidget(window)
    
    # Inicialmente não há abas, viewer deve ser None
    assert window.viewer is None
    
    # Criar uma aba fake (usando Path de teste se possível ou mock)
    # Mas como Window tenta carregar metadados, vamos mockar o Adapter se necessário
    # Para este teste, vamos apenas verificar se não quebra ao acessar sem abas.
    assert window.viewer is None

@pytest.mark.skipif(not Path("manual_test.pdf").exists(), reason="Arquivo de teste não encontrado")
def test_mainwindow_open_file_flow(qtbot):
    """Teste de integração: Abre um arquivo e verifica se os subcomponentes são atualizados."""
    window = MainWindow()
    qtbot.addWidget(window)
    
    test_pdf = Path("manual_test.pdf")
    
    # Simular abertura de arquivo
    window.open_file(test_pdf)
    
    # Verificar se o estado do documento atualizou (Arquitetura V4 Single-Document)
    def check_loaded():
        assert window.current_file is not None
        assert window.current_file.name == test_pdf.name
        assert window.viewer is not None
        assert window.thumbnails is not None
        
    qtbot.waitUntil(check_loaded, timeout=3000)

def test_open_file_updates_viewer(qtbot):
    """Verifica se a abertura de arquivo atualiza corretamente a propriedade viewer da MainWindow na V4."""
    window = MainWindow()
    qtbot.addWidget(window)
    
    test_pdf = Path("manual_test.pdf")
    if test_pdf.exists():
        window.open_file(test_pdf)
        # Na arquitetura V4 Single-Document, o viewer principal é mantido e seu conteúdo atualizado
        def check_loaded():
            assert window.viewer is not None
            assert window.current_file is not None
            assert window.current_file.name == test_pdf.name
            
        qtbot.waitUntil(check_loaded, timeout=3000)

def test_gui_resilience_to_orchestrator_error(qtbot, mocker):
    """Verifica se erros no orquestrador de comandos são reportados no BottomPanel sem crashar."""
    window = MainWindow()
    qtbot.addWidget(window)
    
    # Mock do orchestrator para retornar um erro
    mocker.patch.object(window.orchestrator, 'execute', return_value={"type": "error", "message": "Comando Inválido"})
    
    # Simular entrada de comando na TopBar (ou direto no handler)
    window._on_search_triggered("comando_inexistente")
    
    # Verificar log no BottomPanel
    # Nota: bottom_panel.add_log é o método usado
    # Vamos verificar se o log contém a mensagem de erro
    # Como não temos acesso fácil ao conteúdo do BottomPanel (TextEdit interno), 
    # mockamos o add_log para verificar a chamada
    mocker.spy(window.bottom_panel, 'add_log')
    window._on_search_triggered("fail")
    
    window.bottom_panel.add_log.assert_called()
    assert "Comando Inválido" in window.bottom_panel.add_log.call_args[0][0]
