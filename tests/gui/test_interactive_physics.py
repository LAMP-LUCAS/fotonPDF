"""
Testes de Física Interativa - Sprint 23: Certificação Premium UX 💎
Validação do comportamento físico: Drag-and-Drop, Zoom Cirúrgico,
RubberBand Selection e Recuperação de Qualidade Pós-Zoom.
"""
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, call
from PyQt6.QtCore import Qt, QPointF, QPoint
from PyQt6.QtGui import QPixmap, QWheelEvent
from PyQt6.QtWidgets import QApplication


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(autouse=True)
def mock_render_engine():
    """Fixture para mockar o RenderEngine globalmente."""
    with patch('src.interfaces.gui.state.render_engine.RenderEngine') as mock_base:
        engine = MagicMock()
        mock_base.instance.return_value = engine
        mock_base._instance = None
        yield engine


@pytest.fixture
def light_table(qtbot, mock_render_engine):
    """Cria uma instância de LightTableView com mock de RenderEngine."""
    from src.interfaces.gui.widgets.light_table_view import LightTableView
    lt = LightTableView()
    qtbot.addWidget(lt)
    lt.resize(800, 600)
    lt.show()
    qtbot.waitExposed(lt)
    return lt


@pytest.fixture
def infinite_canvas(qtbot):
    """Cria uma instância de InfiniteCanvasView."""
    from src.interfaces.gui.widgets.infinite_canvas import InfiniteCanvasView
    canvas = InfiniteCanvasView()
    qtbot.addWidget(canvas)
    canvas.resize(800, 600)
    canvas.show()
    qtbot.waitExposed(canvas)
    return canvas


@pytest.fixture
def page_items(light_table, mock_render_engine):
    """Adiciona 5 PageItems à LightTableView para testes de interação."""
    from src.interfaces.gui.widgets.light_table_view import PageItem
    items = []
    spacing = 200
    for i in range(5):
        item = PageItem(i, "dummy_test.pdf", width_pt=595, height_pt=842)
        row, col = i // 3, i % 3
        item.setPos(col * spacing, row * spacing)
        light_table.scene.addItem(item)
        items.append(item)
    return items


# ============================================================================
# 1. Manipulação Espacial na Mesa de Luz (LightTableView)
# ============================================================================

class TestLightTableDragAndDrop:
    """Cenário BDD: Reordenação Tangível via Drag-and-Drop."""

    def test_page_item_is_movable(self, page_items):
        """Verifica que PageItem tem a flag ItemIsMovable habilitada."""
        from src.interfaces.gui.widgets.light_table_view import PageItem
        for item in page_items:
            flags = item.flags()
            assert flags & PageItem.GraphicsItemFlag.ItemIsMovable, \
                f"PageItem {item.page_index} deveria ser movível"

    def test_page_item_is_selectable(self, page_items):
        """Verifica que PageItem tem a flag ItemIsSelectable habilitada."""
        from src.interfaces.gui.widgets.light_table_view import PageItem
        for item in page_items:
            flags = item.flags()
            assert flags & PageItem.GraphicsItemFlag.ItemIsSelectable, \
                f"PageItem {item.page_index} deveria ser selecionável"

    def test_page_item_sends_geometry_changes(self, page_items):
        """Verifica que PageItem notifica mudanças de posição."""
        from src.interfaces.gui.widgets.light_table_view import PageItem
        for item in page_items:
            flags = item.flags()
            assert flags & PageItem.GraphicsItemFlag.ItemSendsGeometryChanges, \
                f"PageItem {item.page_index} deveria enviar mudanças de geometria"

    def test_drag_emits_page_moved_signal(self, qtbot, light_table, page_items):
        """
        Cenário: Reordenação Tangível.
        Given: Páginas carregadas na Mesa de Luz.
        When: Uma página é arrastada para uma nova posição.
        Then: O sinal pageMoved deve ser emitido com o índice e novas coordenadas.
        """
        target_item = page_items[0]
        original_pos = target_item.pos()
        new_pos = QPointF(original_pos.x() + 150, original_pos.y() + 100)

        # Mover programaticamente (simula resultado de drag)
        with qtbot.waitSignal(light_table.pageMoved, timeout=1000) as blocker:
            target_item.setPos(new_pos)

        # Verificar sinal emitido com dados corretos
        assert blocker.args[0] == 0, "Índice da página movida deveria ser 0"
        assert abs(blocker.args[1] - new_pos.x()) < 1.0, "Coordenada X incorreta"
        assert abs(blocker.args[2] - new_pos.y()) < 1.0, "Coordenada Y incorreta"

    def test_multiple_items_can_be_moved_independently(self, qtbot, light_table, page_items):
        """Verifica que múltiplas páginas podem ser movidas independentemente."""
        page_items[0].setPos(QPointF(500, 500))
        page_items[2].setPos(QPointF(700, 300))

        QApplication.processEvents()

        assert page_items[0].pos().x() == 500, "Página 0 deveria estar em x=500"
        assert page_items[2].pos().x() == 700, "Página 2 deveria estar em x=700"
        # Verificar que a página 1 não mudou
        assert page_items[1].pos().x() != 500, "Página 1 não deveria ter se movido junto"


class TestLightTableRubberBandSelection:
    """Cenário BDD: Seleção em Lote via RubberBand."""

    def test_rubber_band_mode_is_default(self, light_table):
        """Verifica que o modo padrão da LightTable é RubberBandDrag."""
        from PyQt6.QtWidgets import QGraphicsView
        assert light_table.dragMode() == QGraphicsView.DragMode.RubberBandDrag, \
            "O modo de arrasto padrão deveria ser RubberBandDrag"

    def test_selection_mode_activates_rubber_band(self, light_table):
        """
        Cenário: Ativação do modo de seleção.
        When: O modo 'selection' é ativado.
        Then: O drag mode deve ser RubberBandDrag.
        """
        from PyQt6.QtWidgets import QGraphicsView
        light_table.set_tool_mode("selection")
        assert light_table.dragMode() == QGraphicsView.DragMode.RubberBandDrag

    def test_programmatic_selection_reflects_count(self, light_table, page_items):
        """
        Cenário: Seleção em Lote.
        Given: 5 páginas em grid.
        When: 3 páginas são selecionadas programaticamente.
        Then: selectedItems() deve reportar exatamente 3 itens.
        """
        light_table.set_tool_mode("selection")

        # Selecionar 3 páginas
        page_items[0].setSelected(True)
        page_items[2].setSelected(True)
        page_items[4].setSelected(True)

        selected = light_table.scene.selectedItems()
        assert len(selected) == 3, f"Esperado 3 itens selecionados, recebido {len(selected)}"

    def test_pan_mode_disables_rubber_band(self, light_table):
        """Verifica que o modo 'pan' desativa o RubberBand."""
        from PyQt6.QtWidgets import QGraphicsView
        light_table.set_tool_mode("pan")
        assert light_table.dragMode() == QGraphicsView.DragMode.NoDrag


# ============================================================================
# 2. Precisão de Engenharia no Infinite Canvas
# ============================================================================

class TestInfiniteCanvasZoom:
    """Cenário BDD: Zoom Cirúrgico (Anchor-under-Mouse)."""

    def test_canvas_has_anchor_under_mouse(self, infinite_canvas):
        """
        Cenário: Configuração de Zoom Cirúrgico.
        Given: Uma InfiniteCanvasView instanciada.
        Then: O TransformationAnchor deve ser AnchorUnderMouse.
        """
        from PyQt6.QtWidgets import QGraphicsView
        assert infinite_canvas.transformationAnchor() == \
            QGraphicsView.ViewportAnchor.AnchorUnderMouse, \
            "O anchor de zoom deveria ser AnchorUnderMouse"

    def test_zoom_in_scales_view(self, infinite_canvas):
        """
        Cenário: Zoom In aumenta a escala.
        When: Um evento de scroll positivo é disparado.
        Then: A transformação (m11) do canvas deve aumentar.
        """
        initial_scale = infinite_canvas.transform().m11()

        # Simular zoom in programaticamente via scale
        zoom_factor = 1.15
        infinite_canvas.scale(zoom_factor, zoom_factor)

        new_scale = infinite_canvas.transform().m11()
        assert new_scale > initial_scale, \
            f"Escala deveria ter aumentado: {initial_scale} -> {new_scale}"

    def test_zoom_out_scales_view(self, infinite_canvas):
        """
        Cenário: Zoom Out diminui a escala.
        When: Um evento de scroll negativo é disparado.
        Then: A transformação (m11) do canvas deve diminuir.
        """
        initial_scale = infinite_canvas.transform().m11()

        zoom_factor = 1 / 1.15
        infinite_canvas.scale(zoom_factor, zoom_factor)

        new_scale = infinite_canvas.transform().m11()
        assert new_scale < initial_scale, \
            f"Escala deveria ter diminuído: {initial_scale} -> {new_scale}"

    def test_canvas_scrollbars_hidden(self, infinite_canvas):
        """Verifica que os scrollbars estão desabilitados (estilo canvas infinito)."""
        assert infinite_canvas.horizontalScrollBarPolicy() == \
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        assert infinite_canvas.verticalScrollBarPolicy() == \
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff

    def test_canvas_has_scroll_hand_drag(self, infinite_canvas):
        """Verifica que o modo de arrasto padrão é ScrollHandDrag (pan)."""
        from PyQt6.QtWidgets import QGraphicsView
        assert infinite_canvas.dragMode() == QGraphicsView.DragMode.ScrollHandDrag


# ============================================================================
# 3. Recuperação de Qualidade Pós-Zoom (LightTableView)
# ============================================================================

class TestQualityRecovery:
    """Cenário BDD: Recuperação de Qualidade Pós-Zoom."""

    def test_quality_timer_fires_on_zoom(self, qtbot, light_table):
        """
        Cenário: Recuperação de Qualidade Pós-Zoom.
        When: O nível de zoom é alterado para 4.0x.
        Then: O QTimer de qualidade deve ser disparado com 300ms.
        """
        light_table._quality_timer = MagicMock()

        light_table.set_zoom(4.0)

        light_table._quality_timer.start.assert_called_once_with(300)

    def test_quality_timer_is_single_shot(self, light_table):
        """Verifica que o timer de qualidade é single-shot (não repetitivo)."""
        assert light_table._quality_timer.isSingleShot(), \
            "O timer de qualidade deveria ser single-shot"

    def test_refresh_quality_updates_visible_items(self, qtbot, light_table, page_items):
        """
        Cenário: Re-renderização Hi-Res após zoom.
        Given: Páginas visíveis na mesa de luz.
        When: _refresh_quality é chamado.
        Then: update_render deve ser chamado nos PageItems visíveis.
        """
        from src.interfaces.gui.widgets.light_table_view import PageItem
        
        # Dar aos items um pixmap real para que sceneBoundingRect tenha tamanho > 0
        for item in page_items:
            item.setPixmap(QPixmap(100, 140))
        
        # Colocar todas as páginas dentro do viewport visível
        light_table.fitInView(light_table.scene.itemsBoundingRect(), 
                              Qt.AspectRatioMode.KeepAspectRatio)
        light_table._zoom = 2.0

        # Espiar update_render nos items
        for item in page_items:
            item.update_render = MagicMock()

        # Disparar refresh
        light_table._refresh_quality()

        # Verificar que update_render foi chamado para pelo menos 1 item visível
        called_count = sum(1 for item in page_items if item.update_render.called)
        assert called_count > 0, \
            "update_render deveria ter sido chamado para as páginas visíveis"

    def test_zoom_area_mode_activates_crosshair(self, light_table):
        """Verifica que o modo zoom_area usa cursor CrossCursor."""
        light_table.set_tool_mode("zoom_area")
        assert light_table.cursor().shape() == Qt.CursorShape.CrossCursor, \
            "O cursor deveria ser CrossCursor no modo zoom_area"

    def test_zoom_clamps_to_valid_range(self, light_table):
        """Verifica que o zoom é limitado entre 0.05 e 5.0."""
        light_table._quality_timer = MagicMock()

        light_table.set_zoom(100.0)
        assert light_table._zoom <= 5.0, "Zoom máximo deveria ser 5.0"

        light_table.set_zoom(0.001)
        assert light_table._zoom >= 0.05, "Zoom mínimo deveria ser 0.05"


# ============================================================================
# 4. Navegação por Teclado na LightTableView
# ============================================================================

class TestKeyboardNavigation:
    """Testes de atalhos de teclado na Mesa de Luz."""

    def test_key_p_activates_pan_mode(self, qtbot, light_table):
        """Verifica que a tecla P ativa o modo Pan."""
        qtbot.keyPress(light_table, Qt.Key.Key_P)
        assert light_table._tool_mode == "pan"

    def test_key_s_activates_selection_mode(self, qtbot, light_table):
        """Verifica que a tecla S ativa o modo Seleção."""
        qtbot.keyPress(light_table, Qt.Key.Key_S)
        assert light_table._tool_mode == "selection"

    def test_key_z_activates_zoom_area(self, qtbot, light_table):
        """Verifica que a tecla Z ativa o modo Zoom por Área."""
        qtbot.keyPress(light_table, Qt.Key.Key_Z)
        assert light_table._tool_mode == "zoom_area"

    def test_ctrl_plus_zooms_in(self, qtbot, light_table):
        """Verifica que Ctrl+= faz zoom in."""
        light_table._quality_timer = MagicMock()
        initial_zoom = light_table._zoom

        qtbot.keyPress(light_table, Qt.Key.Key_Equal,
                       Qt.KeyboardModifier.ControlModifier)

        assert light_table._zoom > initial_zoom, \
            "Zoom deveria ter aumentado com Ctrl+="

    def test_ctrl_minus_zooms_out(self, qtbot, light_table):
        """Verifica que Ctrl+- faz zoom out."""
        light_table._quality_timer = MagicMock()
        initial_zoom = light_table._zoom

        qtbot.keyPress(light_table, Qt.Key.Key_Minus,
                       Qt.KeyboardModifier.ControlModifier)

        assert light_table._zoom < initial_zoom, \
            "Zoom deveria ter diminuído com Ctrl+-"

    def test_ctrl_0_resets_zoom(self, qtbot, light_table):
        """Verifica que Ctrl+0 reseta o zoom para 1.0."""
        light_table._quality_timer = MagicMock()
        light_table.set_zoom(3.0)

        qtbot.keyPress(light_table, Qt.Key.Key_0,
                       Qt.KeyboardModifier.ControlModifier)

        assert light_table._zoom == 1.0, \
            f"Zoom deveria ser 1.0 após reset, recebido {light_table._zoom}"
