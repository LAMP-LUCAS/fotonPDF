import pytest
import inspect
from src.interfaces.gui.main_window import MainWindow

def test_mainwindow_signal_handler_integrity(qtbot, mocker):
    """
    Verifica se todos os métodos de handler (começando com _on_) referenciados 
    em conexões existem de fato na MainWindow.
    """
    # Mock infra to avoid hangs
    mocker.patch("src.infrastructure.services.resource_service.ResourceService.get_logo_ico")
    mocker.patch("src.infrastructure.services.settings_service.SettingsService.instance")
    
    window = MainWindow()
    qtbot.addWidget(window)
    
    # 1. Verificar atributos críticos explicitamente
    critical_attrs = [
        'tabs', 'side_bar', 'side_bar_right', 'bottom_panel', 
        'activity_bar', 'top_bar', 'light_table', 'orchestrator',
        'state_manager'
    ]
    for attr in critical_attrs:
        assert hasattr(window, attr), f"Atributo {attr} não foi inicializado na MainWindow"

    # 2. Verificar conexão de sinais via inspeção de código (Simulado)
    # Como o Qt não expõe facilmente o destino de uma conexão de sinal em Python,
    # vamos validar os métodos que SABEMOS que são usados em _setup_connections_v4 e outros.
    
    expected_handlers = [
        '_on_tab_changed',
        '_on_activity_clicked',
        '_on_search_triggered',
        '_on_layout_toggle_requested',
        '_on_pages_reordered',
        '_on_light_table_moved',
        '_on_open_clicked',
        '_on_save_clicked',
        '_on_save_as_clicked',
        '_on_merge_clicked',
        '_on_extract_clicked',
        '_on_rotate_clicked',
        '_on_highlight_toggled',
        '_on_back_clicked',
        '_on_forward_clicked',
        '_on_ocr_area_toggled',
    ]
    
    for handler in expected_handlers:
        assert hasattr(window, handler), f"Handler referenciado '{handler}' não está implementado na MainWindow"
        method = getattr(window, handler)
        assert callable(method), f"Atributo '{handler}' não é um método chamável"

def test_mainwindow_properties_integrity(qtbot, mocker):
    """Verifica se as propriedades dinâmicas da MainWindow respondem corretamente."""
    mocker.patch("src.infrastructure.services.resource_service.ResourceService.get_logo_ico")
    mocker.patch("src.infrastructure.services.settings_service.SettingsService.instance")
    
    window = MainWindow()
    qtbot.addWidget(window)
    
    # Propriedades de acesso dinâmico
    assert hasattr(MainWindow, 'viewer') and isinstance(MainWindow.viewer, property)
    assert hasattr(MainWindow, 'current_editor_group') and isinstance(MainWindow.current_editor_group, property)
    
    # Valores iniciais (sem abas)
    assert window.viewer is None
    assert window.current_editor_group is None
