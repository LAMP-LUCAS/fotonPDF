from abc import ABC, abstractmethod

class OSIntegrationPort(ABC):
    """Porta para integração com o Shell do Sistema Operacional."""

    @abstractmethod
    def register_context_menu(self) -> bool:
        """Registra a aplicação no menu de contexto de arquivos PDF."""
        pass

    @abstractmethod
    def unregister_context_menu(self) -> bool:
        """Remove a aplicação do menu de contexto."""
        pass
