"""
Testes de Usabilidade Core - Zoom, Seleção de Texto e Mesa de Luz
Sprint 22 - Certificação de Qualidade do Core
"""
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(autouse=True)
def mock_render_engine():
    """Fixture para mockar o RenderEngine globalmente."""
    with patch('src.interfaces.gui.state.render_engine.RenderEngine') as mock:
        engine = MagicMock()
        engine.instance.return_value = engine
        mock.instance.return_value = engine
        yield engine


@pytest.fixture
def mock_pymupdf_adapter():
    """Fixture para mockar o PyMuPDFAdapter."""
    with patch('src.infrastructure.adapters.pymupdf_adapter.PyMuPDFAdapter') as mock:
        adapter = MagicMock()
        adapter.get_text_in_rect.return_value = "Texto extraído de teste"
        mock.return_value = adapter
        yield adapter


# ============================================================================
# Testes de Zoom com Re-Render
# ============================================================================

class TestZoomRerender:
    """Testes para garantir que zoom força re-renderização."""
    
    def test_page_widget_resets_rendered_on_zoom_change(self, qtbot):
        """Verifica que PageWidget.update_layout_size reseta _rendered."""
        from src.interfaces.gui.widgets.page_widget import PageWidget
        
        page = PageWidget("dummy.pdf", 0, width_pt=595, height_pt=842)
        qtbot.addWidget(page)
        
        # Simular estado "já renderizado"
        page._rendered = True
        page._base_pixmap = QPixmap(100, 100)
        
        # Mudar zoom
        page.update_layout_size(2.0)
        
        # Verificar que foi marcado como não renderizado
        assert page._rendered == False, "Widget deveria estar marcado como não renderizado após mudança de zoom"
        assert page._base_pixmap is None, "Pixmap deveria ser invalidado"
    
    def test_zoom_change_triggers_render_request(self, qtbot, mock_render_engine):
        """Verifica que mudança de zoom dispara request_render."""
        from src.interfaces.gui.widgets.page_widget import PageWidget
        
        page = PageWidget("dummy.pdf", 0, width_pt=595, height_pt=842)
        qtbot.addWidget(page)
        
        # Renderizar com zoom 1.0
        page.render_page(zoom=1.0)
        mock_render_engine.request_render.assert_called()
        
        # Reset mock
        mock_render_engine.request_render.reset_mock()
        
        # Renderizar com zoom 2.0
        page.render_page(zoom=2.0)
        
        # Verificar que request_render foi chamado com o novo zoom
        mock_render_engine.request_render.assert_called()
        call_args = mock_render_engine.request_render.call_args
        # O zoom é o terceiro argumento posicional
        assert call_args[0][2] == 2.0, f"Esperado zoom=2.0, recebido {call_args[0][2]}"


# ============================================================================
# Testes de Mesa de Luz Hi-Res
# ============================================================================

class TestLightTableHiRes:
    """Testes para garantir qualidade Hi-Res na Mesa de Luz."""
    
    def test_page_item_allows_high_zoom_render(self, qtbot, mock_render_engine):
        """Verifica que PageItem permite renderização até 3x."""
        from src.interfaces.gui.widgets.light_table_view import PageItem
        
        item = PageItem(0, "dummy.pdf", 595, 842)
        
        # Solicitar render com zoom 2.5 (antes era limitado a 1.5)
        item.update_render(2.5)
        
        # Verificar que request_render foi chamado com zoom >= 2.5
        mock_render_engine.request_render.assert_called()
        call_args = mock_render_engine.request_render.call_args
        # O zoom é o terceiro argumento
        actual_zoom = call_args[0][2]
        assert actual_zoom >= 2.5, f"Zoom mínimo esperado: 2.5, recebido: {actual_zoom}"
    
    def test_light_table_refreshes_quality_on_zoom(self, qtbot, mock_render_engine):
        """Verifica que o timer de qualidade é disparado ao fazer zoom."""
        from src.interfaces.gui.widgets.light_table_view import LightTableView
        
        lt = LightTableView()
        qtbot.addWidget(lt)
        
        # Spy no timer de qualidade
        lt._quality_timer = MagicMock()
        
        # Fazer zoom
        lt.set_zoom(2.0)
        
        # Verificar que o timer foi inicializado
        lt._quality_timer.start.assert_called()


# ============================================================================
# Testes de Seleção de Texto
# ============================================================================

class TestTextSelection:
    """Testes para funcionalidade de seleção e extração de texto."""
    
    def test_viewer_widget_has_selection_signals(self, qtbot):
        """Verifica que PDFViewerWidget tem os sinais de seleção."""
        from src.interfaces.gui.widgets.viewer_widget import PDFViewerWidget
        
        viewer = PDFViewerWidget()
        qtbot.addWidget(viewer)
        
        assert hasattr(viewer, 'selectionChanged'), "Falta sinal selectionChanged"
        assert hasattr(viewer, 'textExtracted'), "Falta sinal textExtracted"
    
    def test_pymupdf_adapter_has_get_text_in_rect(self):
        """Verifica que PyMuPDFAdapter tem método get_text_in_rect."""
        from src.infrastructure.adapters.pymupdf_adapter import PyMuPDFAdapter
        
        adapter = PyMuPDFAdapter()
        assert hasattr(adapter, 'get_text_in_rect'), "Falta método get_text_in_rect"
        assert callable(adapter.get_text_in_rect), "get_text_in_rect deveria ser chamável"


# ============================================================================
# Testes de Persistência de Notas (Placeholder)
# ============================================================================

class TestAnnotationsPersistence:
    """Testes para o painel de anotações."""
    
    def test_annotations_panel_exists(self, qtbot):
        """Verifica que AnnotationsPanel pode ser instanciado."""
        from src.interfaces.gui.widgets.annotations_panel import AnnotationsPanel
        
        panel = AnnotationsPanel()
        qtbot.addWidget(panel)
        
        assert panel is not None
        # Verificar sinais básicos
        assert hasattr(panel, 'annotationClicked'), "Falta sinal annotationClicked"
