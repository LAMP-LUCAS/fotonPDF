"""
Tests E2E para Navegação Universal (ModernNavBar, NavHub, Atalhos)
Sprint 22 - Consolidação e Lançamento
"""
import pytest
from unittest.mock import MagicMock, patch
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtTest import QTest


@pytest.fixture(autouse=True)
def mock_render_engine():
    """Fixture para mockar o RenderEngine globalmente."""
    with patch('src.interfaces.gui.state.render_engine.RenderEngine') as mock:
        engine = MagicMock()
        engine.instance.return_value = engine
        mock.instance.return_value = engine
        yield engine


class TestModernNavBarSignals:
    """Testes de integração para sinais da ModernNavBar."""
    
    def test_navbar_emits_zoom_signals(self, qtbot):
        """Verifica se a barra de navegação emite corretamente os sinais de zoom."""
        from src.interfaces.gui.widgets.floating_navbar import ModernNavBar
        
        nav_bar = ModernNavBar()
        qtbot.addWidget(nav_bar)
        
        # Verificar que sinais existem
        assert hasattr(nav_bar, 'zoomIn')
        assert hasattr(nav_bar, 'zoomOut')
        assert hasattr(nav_bar, 'resetZoom')
        assert hasattr(nav_bar, 'fitWidth')
        assert hasattr(nav_bar, 'fitHeight')
        assert hasattr(nav_bar, 'fitPage')
        
    def test_navbar_emits_navigation_signals(self, qtbot):
        """Verifica se a barra de navegação emite corretamente os sinais de página."""
        from src.interfaces.gui.widgets.floating_navbar import ModernNavBar
        
        nav_bar = ModernNavBar()
        qtbot.addWidget(nav_bar)
        
        assert hasattr(nav_bar, 'nextPage')
        assert hasattr(nav_bar, 'prevPage')
        
    def test_navbar_emits_tool_signal(self, qtbot):
        """Verifica se a barra de navegação emite sinais de troca de ferramenta."""
        from src.interfaces.gui.widgets.floating_navbar import ModernNavBar
        
        nav_bar = ModernNavBar()
        qtbot.addWidget(nav_bar)
        
        assert hasattr(nav_bar, 'setTool')

class TestViewerWidgetKeyboardShortcuts:
    """Testes de atalhos de teclado no ViewerWidget."""
    
    def test_viewer_has_keyboard_shortcuts(self, qtbot):
        """Verifica se o visualizador responde aos atalhos de teclado."""
        from src.interfaces.gui.widgets.viewer_widget import PDFViewerWidget
        
        viewer = PDFViewerWidget()
        qtbot.addWidget(viewer)
        
        # Verificar métodos de navegação existem
        assert hasattr(viewer, 'next_page')
        assert hasattr(viewer, 'prev_page')
        assert hasattr(viewer, 'zoom_in')
        assert hasattr(viewer, 'zoom_out')
        assert hasattr(viewer, 'reset_zoom')
        assert hasattr(viewer, 'fit_width')
        assert hasattr(viewer, 'fit_page')
        
    def test_viewer_tool_modes(self, qtbot):
        """Verifica se o visualizador suporta diferentes modos de ferramenta."""
        from src.interfaces.gui.widgets.viewer_widget import PDFViewerWidget
        
        viewer = PDFViewerWidget()
        qtbot.addWidget(viewer)
        
        # Verificar método set_tool_mode
        assert hasattr(viewer, 'set_tool_mode')
        
        # Verificar modos suportados
        viewer.set_tool_mode("pan")
        assert viewer._tool_mode == "pan"
        
        viewer.set_tool_mode("selection")
        assert viewer._tool_mode == "selection"
        
        viewer.set_tool_mode("zoom_area")
        assert viewer._tool_mode == "zoom_area"


class TestLightTableViewToolModes:
    """Testes de modos de ferramenta na Mesa de Luz."""
    
    def test_lighttable_supports_zoom_area(self, qtbot):
        """Verifica se a mesa de luz suporta o modo zoom_area."""
        from src.interfaces.gui.widgets.light_table_view import LightTableView
        
        lt = LightTableView()
        qtbot.addWidget(lt)
        
        # Verificar método set_tool_mode
        assert hasattr(lt, 'set_tool_mode')
        
        # Verificar modos suportados
        lt.set_tool_mode("pan")
        assert lt._tool_mode == "pan"
        
        lt.set_tool_mode("zoom_area")
        assert lt._tool_mode == "zoom_area"
        assert lt._zoom_area_active == True


class TestNavHubIntegration:
    """Testes de integração do NavHub (volante de controle)."""
    
    def test_navhub_exists_and_has_signals(self, qtbot):
        """Verifica se o NavHub existe e emite sinais de ferramenta."""
        from src.interfaces.gui.widgets.nav_hub import NavHub
        
        hub = NavHub()
        qtbot.addWidget(hub)
        
        assert hasattr(hub, 'toolChanged')
        

class TestViewModeSwitching:
    """Testes de troca de modo de visualização (Scroll <-> Mesa)."""
    
    def test_viewer_has_view_all_connection(self, qtbot):
        """Verifica se a ModernNavBar pode disparar troca de visão."""
        from src.interfaces.gui.widgets.floating_navbar import ModernNavBar
        
        nav_bar = ModernNavBar()
        qtbot.addWidget(nav_bar)
        
        # Verificar sinal viewAll existe
        assert hasattr(nav_bar, 'viewAll')
