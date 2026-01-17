from abc import ABC, abstractmethod

class NotificationPort(ABC):
    """Porta para envio de notificações ao usuário."""

    @abstractmethod
    def notify(self, title: str, message: str):
        """Exibe uma notificação nativa."""
        pass
