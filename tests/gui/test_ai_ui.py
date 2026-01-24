import pytest
from PyQt6.QtWidgets import QApplication
from src.interfaces.gui.widgets.ai_settings_panel import AISettingsWidget
from src.infrastructure.services.settings_service import SettingsService

def test_ai_settings_ui_persistence(qtbot):
    """Verifica se a UI de configurações de IA salva os dados corretamente."""
    widget = AISettingsWidget()
    qtbot.addWidget(widget)
    
    # Preencher campos
    widget.combo_provider.setCurrentText("openai")
    widget.edit_model.setText("gpt-4o")
    widget.edit_key.setText("sk-test-key")
    
    # Clicar em salvar
    qtbot.mouseClick(widget.btn_save, qtbot.Qt.MouseButton.LeftButton)
    
    # Verificar persistência no SettingsService
    settings = SettingsService.instance()
    assert settings.get("ai_provider") == "openai"
    assert settings.get("ai_model") == "gpt-4o"
    assert settings.get("ai_api_key") == "sk-test-key"

def test_ai_config_placeholder_labels(qtbot):
    """Valida se as labels de configuração de IA estão presentes."""
    widget = AISettingsWidget()
    qtbot.addWidget(widget)
    
    assert "CONFIGURAÇÃO DE INTELIGÊNCIA" in widget.findChild(qtbot.QtWidgets.QLabel).text()
