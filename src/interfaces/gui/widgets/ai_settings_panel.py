from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QComboBox, QPushButton, QFormLayout, QFrame, QCheckBox)
from PyQt6.QtCore import Qt
from src.infrastructure.services.settings_service import SettingsService

class AISettingsWidget(QWidget):
    """
    Interface de configuração de IA do fotonPDF.
    Permite alternar entre Ollama e Cloud APIs com segurança e privacidade.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._settings = SettingsService.instance()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = QLabel("CONFIGURAÇÃO DE INTELIGÊNCIA")
        title.setStyleSheet("color: #FFC107; font-weight: bold; font-size: 14px;")
        layout.addWidget(title)

        # Ativar Assistente
        self.check_enabled = QCheckBox("Ativar Assistente de IA")
        self.check_enabled.setChecked(self._settings.get_bool("ai_enabled", False))
        self.check_enabled.setStyleSheet("color: white; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(self.check_enabled)

        # Frame para agrupar campos (opcionalmente desabilitar se checkbox for false)
        self.config_frame = QFrame()
        form = QFormLayout(self.config_frame)
        form.setSpacing(10)

        # Provedor
        self.combo_provider = QComboBox()
        self.combo_provider.addItems(["ollama", "openai", "openrouter", "google"])
        self.combo_provider.setCurrentText(self._settings.get("ai_provider", "ollama"))
        form.addRow("Provedor:", self.combo_provider)

        # Modelo
        self.edit_model = QLineEdit()
        self.edit_model.setPlaceholderText("ex: llama3, gpt-4o-mini")
        self.edit_model.setText(self._settings.get("ai_model", "llama3"))
        form.addRow("Modelo:", self.edit_model)

        # API Key (com máscara)
        self.edit_key = QLineEdit()
        self.edit_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.edit_key.setText(self._settings.get("ai_api_key", ""))
        form.addRow("API Key:", self.edit_key)

        # Base URL (para Ollama)
        self.edit_url = QLineEdit()
        self.edit_url.setText(self._settings.get("ai_base_url", "http://localhost:11434"))
        form.addRow("Base URL:", self.edit_url)

        layout.addWidget(self.config_frame)

        # Conectar sinal para habilitar/desabilitar campos
        self.check_enabled.toggled.connect(self.config_frame.setEnabled)
        self.config_frame.setEnabled(self.check_enabled.isChecked())

        # Botão Salvar
        self.btn_save = QPushButton("Salvar Configurações")
        self.btn_save.setStyleSheet("""
            QPushButton { background-color: #334155; color: white; padding: 10px; border-radius: 6px; }
            QPushButton:hover { background-color: #FFC107; color: #0F172A; }
        """)
        self.btn_save.clicked.connect(self._save_settings)
        layout.addWidget(self.btn_save)
        
        layout.addStretch()

    def _save_settings(self):
        self._settings.set("ai_enabled", self.check_enabled.isChecked())
        self._settings.set("ai_provider", self.combo_provider.currentText())
        self._settings.set("ai_model", self.edit_model.text())
        self._settings.set("ai_api_key", self.edit_key.text())
        self._settings.set("ai_base_url", self.edit_url.text())
        
        # Notificar MainWindow de que os modelos precisam ser recarregados (via signals se necessário)
        self.btn_save.setText("✅ Configurações Salvas!")
        self.btn_save.setStyleSheet("background-color: #059669; color: white; padding: 10px; border-radius: 6px;")
