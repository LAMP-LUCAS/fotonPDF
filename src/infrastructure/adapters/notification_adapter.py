from plyer import notification
from src.domain.ports.notification import NotificationPort

class PlyerNotificationAdapter(NotificationPort):
    """Implementação de notificações usando a biblioteca cross-platform plyer."""

    def notify(self, title: str, message: str):
        try:
            notification.notify(
                title=title,
                message=message,
                app_name='fotonPDF',
                app_icon=None,
                timeout=5
            )
        except Exception as e:
            # Fallback silencioso ou log no console se notificação falhar
            print(f"⚠️ Alerta (Notificação falhou): {title} - {message} ({e})")
