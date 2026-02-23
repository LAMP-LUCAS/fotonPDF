import sys
from pathlib import Path

class ResourceService:
    """Serviço para gerenciar caminhos de recursos de forma robusta entre Dev e Produção."""

    @staticmethod
    def get_resource_path(relative_path: str) -> Path:
        """
        Retorna o caminho absoluto para um recurso, funcionando em modo dev e frozen (PyInstaller).
        
        O PyInstaller extrai arquivos para uma pasta temporária e armazena o caminho em sys._MEIPASS.
        """
        if getattr(sys, 'frozen', False):
            # No modo onedir/onefile do PyInstaller, sys._MEIPASS aponta para a pasta base dos recursos
            base_path = Path(sys._MEIPASS)
        else:
            # No modo desenvolvimento, a base é a raíz do projeto
            # Assumindo que este serviço está em src/infrastructure/services/resource_service.py
            base_path = Path(__file__).parents[3]

        return base_path / relative_path

    @staticmethod
    def get_logo_svg() -> Path:
        return ResourceService.get_resource_path("docs/brand/logo.svg")

    @staticmethod
    def get_logo_ico() -> Path:
        """Retorna o ícone principal da aplicação (ICO/PNG/SVG)."""
        # Priorizar assets gerados na pasta de documentação/brand
        ico_path = ResourceService.get_resource_path("docs/brand/logo.ico")
        if ico_path.exists():
            return ico_path
        
        # Fallback para ícones de recurso interno se existirem
        internal_png = ResourceService.get_resource_path("src/resources/icons/logo.png")
        if internal_png.exists():
            return internal_png
            
        return ico_path # Retorna path do ico mesmo que não exista (fallback final)
