from src.domain.ports.os_integration import OSIntegrationPort

class UnregisterOSIntegrationUseCase:
    """Caso de uso para remover o registro do fotonPDF no SO."""

    def __init__(self, os_port: OSIntegrationPort):
        self._os_port = os_port

    def execute(self) -> bool:
        """Executa a remoção completa: menu de contexto e atalhos."""
        success = True
        
        # 1. Remover Menu de Contexto
        if not self._os_port.unregister_context_menu():
            success = False
            
        # 2. Remover Atalhos (Best effort)
        self._os_port.remove_shortcut("desktop")
        self._os_port.remove_shortcut("start_menu")
        
        return success
