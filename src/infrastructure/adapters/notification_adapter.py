from plyer import notification
from src.domain.ports.notification import NotificationPort

class PlyerNotificationAdapter(NotificationPort):
    """Implementação de notificações usando a biblioteca cross-platform plyer."""

    def notify(self, title: str, message: str):
        notification.notify(
            title=title,
            message=message,
            app_name='fotonPDF',
            app_icon=None,  # Podemos adicionar ícones depois
            timeout=5
        )
