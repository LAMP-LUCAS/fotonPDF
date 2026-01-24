from abc import ABC, abstractmethod

class UISettingsPort(ABC):
    """ Porta para persistência de configurações de interface (Hexagonal Architecture). """

    @abstractmethod
    def save_window_state(self, geometry: bytes, state: bytes):
        """ Salva a geometria e o estado da janela. """
        pass

    @abstractmethod
    def load_window_state(self) -> tuple[bytes, bytes]:
        """ Retorna (geometry, state) da janela. """
        pass

    @abstractmethod
    def set(self, key: str, value):
        """ Salva uma configuração genérica. """
        pass

    @abstractmethod
    def get(self, key: str, default=None):
        """ Recupera uma configuração genérica. """
        pass
