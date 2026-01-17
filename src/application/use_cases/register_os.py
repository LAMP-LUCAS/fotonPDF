from src.domain.ports.os_integration import OSIntegrationPort

class RegisterOSIntegrationUseCase:
    """Caso de uso para registrar as funcionalidades do fotonPDF no SO."""

    def __init__(self, os_port: OSIntegrationPort):
        self._os_port = os_port

    def execute(self) -> bool:
        """Executa o registro no menu de contexto."""
        return self._os_port.register_context_menu()
