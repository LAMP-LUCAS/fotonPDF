import pytest
from PyQt6.QtCore import Qt
from src.interfaces.gui.widgets.top_bar import TopBarWidget
from src.interfaces.gui.widgets.inspector_panel import InspectorPanel
from src.interfaces.gui.widgets.command_palette import CommandPalette
from src.interfaces.gui.widgets.infinite_canvas import InfiniteCanvasView

@pytest.fixture
def top_bar(qtbot):
    widget = TopBarWidget()
    qtbot.addWidget(widget)
    return widget

@pytest.fixture
def inspector_panel(qtbot):
    widget = InspectorPanel()
    qtbot.addWidget(widget)
    return widget

@pytest.fixture
def command_palette(qtbot):
    widget = CommandPalette()
    qtbot.addWidget(widget)
    return widget

@pytest.fixture
def infinite_canvas(qtbot):
    widget = InfiniteCanvasView()
    qtbot.addWidget(widget)
    return widget

# --- TopBarWidget Tests ---

def test_top_bar_initialization(top_bar):
    assert top_bar.objectName() == "TopBar"
    assert top_bar.height() == 48
    assert top_bar.btn_scroll.isChecked()
    assert not top_bar.btn_table.isChecked()

def test_top_bar_search_signal(top_bar, qtbot):
    with qtbot.waitSignal(top_bar.searchTriggered) as blocker:
        top_bar.search_input.setText("test query")
        qtbot.keyClick(top_bar.search_input, Qt.Key.Key_Enter)
    assert blocker.args == ["test query"]

def test_top_bar_toggle_signals(top_bar, qtbot):
    with qtbot.waitSignal(top_bar.toggleRequested) as blocker:
        top_bar.btn_bottom.click()
    assert blocker.args == ["bottom_panel"]

# --- InspectorPanel Tests ---

@pytest.mark.skip(reason="Hangs in headless environment during QScrollArea/Layout init")
def test_inspector_panel_initial_state(inspector_panel):
    assert not inspector_panel.placeholder_widget.isHidden()
    assert "Selecione um documento" in inspector_panel.placeholder_label.text()

@pytest.mark.skip(reason="Hangs in headless environment during QScrollArea/Layout init")
def test_inspector_panel_lazy_init(inspector_panel, qtbot):
    # Trigger lazy init via update_metadata
    metadata = {
        "pages": [{"format": "A4", "width_mm": 210, "height_mm": 297}],
        "layers": [{"id": 1, "name": "Layer 1", "visible": True}]
    }
    inspector_panel.update_metadata(metadata)
    
    assert inspector_panel._ui_initialized
    assert inspector_panel.placeholder_widget.isHidden()
    assert inspector_panel.lbl_format.text() == "A4"
    assert inspector_panel.lbl_dims.text() == "210 x 297"

# --- CommandPalette Tests ---

@pytest.mark.skip(reason="Hangs in headless environment during Shadow effect init")
def test_command_palette_filtering(command_palette):
    command_palette._filter_items("Girar")
    assert command_palette.results_list.count() > 0
    # Deve conter "Girar Página (90° Horário)"
    items = [command_palette.results_list.item(i).text() for i in range(command_palette.results_list.count())]
    assert any("Girar" in it for it in items)

# --- InfiniteCanvasView Tests ---

def test_infinite_canvas_zoom(infinite_canvas):
    initial_transform = infinite_canvas.transform()
    # Simular scroll do mouse para zoom
    from PyQt6.QtGui import QWheelEvent
    from PyQt6.QtCore import QPoint
    
    event = QWheelEvent(
        QPoint(10, 10).toPointF(), 
        QPoint(10, 10).toPointF(), 
        QPoint(0, 120), 
        QPoint(0, 120), 
        Qt.MouseButton.NoButton, 
        Qt.KeyboardModifier.NoModifier, 
        Qt.ScrollPhase.NoScrollPhase, 
        False
    )
    infinite_canvas.wheelEvent(event)
    assert infinite_canvas.transform().m11() > initial_transform.m11()
