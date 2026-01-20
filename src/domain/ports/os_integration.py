from abc import ABC, abstractmethod

class OSIntegrationPort(ABC):
    """Porta para integração com o Shell do Sistema Operacional."""

    @abstractmethod
    def register_context_menu(self, label: str, command: str) -> bool:
        """Registra a aplicação no menu de contexto de arquivos PDF."""
        pass

    @abstractmethod
    def unregister_context_menu(self) -> bool:
        """Remove a aplicação do menu de contexto."""
        pass

    @abstractmethod
    def create_shortcut(self, location: str) -> bool:
        """
        Cria um atalho para a aplicação.
        Locations: 'desktop', 'start_menu'.
        """
        pass

    @abstractmethod
    def remove_shortcut(self, location: str) -> bool:
        """Remove o atalho da aplicação no local especificado."""
        pass

    @abstractmethod
    def set_as_default_viewer(self) -> bool:
        """Define a aplicação como visualizador padrão para arquivos .pdf."""
        pass

    @abstractmethod
    def register_all_context_menus(self) -> bool:
        """Registra todas as funções padrão no menu de contexto."""
        pass

    @abstractmethod
    def check_installation_status(self) -> bool:
        """Verifica se a integração com o SO está ativa."""
        pass

    @abstractmethod
    def repair_installation(self) -> bool:
        """Tenta reparar chaves de registro ou atalhos corrompidos."""
        pass
