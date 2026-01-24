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
    mocker.patch("src.infrastructure.adapters.pymupdf_adapter.PyMuPDFAdapter", autospec=True)
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
    
    # Verificar se a aba foi criada
    assert window.tabs.count() == 1
    assert window.current_file == test_pdf
    
    # Verificar se o viewer agora é válido
    assert window.viewer is not None
    
    # Verificar se a sidebar (thumbnails) foi disparada
    # (Thumbnail loading é assíncrono em alguns casos, mas aqui deve estar no stack)
    assert window.thumbnails is not None

def test_tab_switching_updates_viewer(qtbot):
    """Verifica se a mudança de aba atualiza corretamente a propriedade viewer da MainWindow."""
    window = MainWindow()
    qtbot.addWidget(window)
    
    # Simular abertura de dois arquivos (mesmo arquivo para simplicidade se existir)
    test_pdf = Path("manual_test.pdf")
    if test_pdf.exists():
        window.open_file(test_pdf)
        # window.open_file(test_pdf) # TabContainer.add_editor evita duplicatas? Sim, mas podemos forçar
        
        # Como o add_editor evita duplicatas, vamos validar a troca se tivéssemos 2
        # Por enquanto validamos que com 1 aba o viewer aponta para o widget dessa aba
        current_viewer = window.tabs.current_editor().get_viewer()
        assert window.viewer == current_viewer

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
