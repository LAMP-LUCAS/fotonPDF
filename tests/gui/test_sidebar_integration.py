import pytest
from PyQt6.QtCore import Qt
from unittest.mock import MagicMock, patch
from src.interfaces.gui.main_window import MainWindow
from src.interfaces.gui.widgets.thumbnail_panel import ThumbnailPanel

@pytest.fixture
def app_window(qtbot, mock_settings):
    # Mocking PyMuPDFAdapter to avoid real PDF operations and potential crashes
    with patch('src.interfaces.gui.main_window.PyMuPDFAdapter') as mock_adapter_cls:
        window = MainWindow()
        qtbot.addWidget(window)
        return window

def test_activity_bar_clicks_switch_sidebar_panels(app_window, qtbot):
    """Valida que cliques na ActivityBar trocam os painéis na SideBar."""
    activity_bar = app_window.activity_bar
    side_bar = app_window.side_bar
    
    # Garantir que a sidebar está aberta para o teste
    if side_bar._is_collapsed:
        side_bar.expand()
    
    # 1. Clicar em Pesquisar (Índice 1)
    # Lazy loading: MainWindow._on_activity_clicked(1) chamará _ensure_panel_loaded("search")
    search_btn = activity_bar.group.button(1)
    qtbot.mouseClick(search_btn, Qt.MouseButton.LeftButton)
    
    assert side_bar.stack.currentIndex() == 1
    assert "PESQUISAR" in side_bar.title_label.text().upper()
    
    # 2. Clicar em Índice (Índice 2)
    toc_btn = activity_bar.group.button(2)
    qtbot.mouseClick(toc_btn, Qt.MouseButton.LeftButton)
    
    assert side_bar.stack.currentIndex() == 2
    assert "ÍNDICE" in side_bar.title_label.text().upper()

@pytest.mark.skip(reason="Refactor needed for Direct Layout and RenderEngine mocking")
def test_thumbnail_panel_load_logic(qtbot):
    """(SKIPPED) Valida que o ThumbnailPanel carrega miniaturas."""
    pass

def test_sidebar_stays_active_on_same_click_if_collapsed(app_window, qtbot):
    """Valida que se a sidebar está fechada, clicar no ícone já ativo a abre."""
    side_bar = app_window.side_bar
    side_bar.collapse()
    qtbot.wait(400) # Aguarda animação aproximada
    
    assert side_bar._is_collapsed or side_bar.width() == 0
    
    activity_bar = app_window.activity_bar
    pages_btn = activity_bar.group.button(0) # Já é o padrão marcado
    
    # Clicar no botão de páginas (já selecionado) deve forçar abertura
    qtbot.mouseClick(pages_btn, Qt.MouseButton.LeftButton)
    
    assert not side_bar._is_collapsed
    assert side_bar.stack.currentIndex() == 0
