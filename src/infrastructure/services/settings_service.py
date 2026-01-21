from PyQt6.QtCore import QSettings
from pathlib import Path
from src.infrastructure.services.logger import log_debug

class SettingsService:
    """Serviço centralizado para persistência de configurações de usuário."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SettingsService, cls).__new__(cls)
            # Organização: fotonPDF -> GUI_Settings
            cls._instance.settings = QSettings("fotonPDF", "Preferences")
        return cls._instance

    @classmethod
    def instance(cls):
        return cls()

    def set(self, key: str, value):
        """Salva uma configuração."""
        log_debug(f"Settings: Salvando {key} = {value}")
        self.settings.setValue(key, value)

    def get(self, key: str, default=None):
        """Recupera uma configuração."""
        return self.settings.value(key, default)

    def get_float(self, key: str, default: float = 0.0) -> float:
        val = self.get(key, default)
        try:
            return float(val)
        except (ValueError, TypeError):
            return default

    def get_bool(self, key: str, default: bool = False) -> bool:
        val = self.get(key, default)
        if isinstance(val, bool):
            return val
        if isinstance(val, str):
            return val.lower() == "true"
        return bool(val)

    def get_int(self, key: str, default: int = 0) -> int:
        val = self.get(key, default)
        try:
            return int(val)
        except (ValueError, TypeError):
            return default
