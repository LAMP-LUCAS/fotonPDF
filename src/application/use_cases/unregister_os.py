from src.domain.ports.os_integration import OSIntegrationPort

class UnregisterOSIntegrationUseCase:
    """Caso de uso para remover o registro do fotonPDF no SO."""

    def __init__(self, os_port: OSIntegrationPort):
        self._os_port = os_port

    def execute(self) -> bool:
        """Executa a remoção do registro no menu de contexto."""
        return self._os_port.unregister_context_menu()
