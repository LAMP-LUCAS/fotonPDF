import pytest
from unittest.mock import MagicMock, patch
from PyQt6.QtCore import Qt
from src.interfaces.gui.widgets.inspector_panel import InspectorPanel
from src.interfaces.gui.main_window import MainWindow

@pytest.fixture
def mock_render_engine():
    with patch('src.interfaces.gui.state.render_engine.RenderEngine') as MockEngine:
        instance = MockEngine.instance.return_value
        yield instance

def test_layer_toggling_isolation(qtbot):
    """
    Testa a lógica do InspectorPanel isoladamente, conectando a um mock.
    """
    # 1. Setup Inspector
    inspector = InspectorPanel()
    qtbot.addWidget(inspector)
    inspector.show()
    
    # 2. Setup Mock Callback
    mock_callback = MagicMock()
    inspector.layerVisibilityChanged.connect(mock_callback)
    
    # 3. Populate Metadata
    layers_data = [
        {"id": 10, "name": "Architecture", "visible": True},
        {"id": 20, "name": "Plumbing", "visible": False}
    ]
    inspector.update_metadata({"layers": layers_data, "pages": [{"format": "A3"}]})
    
    # 4. Force Update (Bypass Timer)
    inspector._deferred_layer_update(layers_data)
    
    # 5. Check Checkboxes
    from PyQt6.QtWidgets import QCheckBox
    checkboxes = inspector.layers_container.findChildren(QCheckBox)
    assert len(checkboxes) == 2
    
    cb_arch = checkboxes[0]
    cb_plumb = checkboxes[1]
    
    assert cb_arch.text() == "Architecture"
    assert cb_arch.isChecked() == True
    
    assert cb_plumb.text() == "Plumbing"
    assert cb_plumb.isChecked() == False
    
    # 6. Toggle Architecture OFF
    cb_arch.setChecked(False)
    
    # 7. Verify Signal
    mock_callback.assert_called_with(10, False)
    
    # 8. Toggle Plumbing ON
    cb_plumb.setChecked(True)
    mock_callback.assert_called_with(20, True)
