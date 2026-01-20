from src.domain.ports.os_integration import OSIntegrationPort

class RegisterOSIntegrationUseCase:
    """Caso de uso para registrar as funcionalidades do fotonPDF no SO."""

    def __init__(self, os_port: OSIntegrationPort):
        self._os_port = os_port

    def execute(self, label: str, command: str) -> bool:
        """Executa o registro de um único item no menu de contexto."""
        return self._os_port.register_context_menu(label, command)

    def register_all(self) -> bool:
        """Registra todas os itens padrão do menu de contexto."""
        return self._os_port.register_all_context_menus()

    def create_shortcut(self, location: str) -> bool:
        """Cria atalho no local especificado."""
        return self._os_port.create_shortcut(location)

    def set_as_default(self) -> bool:
        """Define como programa padrão."""
        return self._os_port.set_as_default_viewer()
