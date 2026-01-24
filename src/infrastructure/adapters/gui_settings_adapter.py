from src.application.ports.ui_settings_port import UISettingsPort
from src.infrastructure.services.settings_service import SettingsService

class GUISettingsAdapter(UISettingsPort):
    """ Implementação concreta do conector de configurações para a GUI. """

    def __init__(self):
        self._service = SettingsService.instance()

    def save_window_state(self, geometry: bytes, state: bytes):
        self._service.set("window_geometry", geometry)
        self._service.set("window_state", state)

    def load_window_state(self) -> tuple[bytes, bytes]:
        geometry = self._service.get("window_geometry")
        state = self._service.get("window_state")
        return geometry, state

    def set(self, key: str, value):
        self._service.set(key, value)

    def get(self, key: str, default=None):
        return self._service.get(key, default)
