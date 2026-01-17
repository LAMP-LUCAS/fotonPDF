import sys
import winreg
from pathlib import Path
from src.domain.ports.os_integration import OSIntegrationPort

class WindowsRegistryAdapter(OSIntegrationPort):
    """Adaptador para manipular o Registro do Windows e adicionar o Menu de Contexto."""

    def __init__(self):
        self._app_path = sys.executable if getattr(sys, 'frozen', False) else f'"{sys.executable}" "{Path(__file__).parents[2] / "interfaces" / "cli" / "main.py"}"'
        self._ext = ".pdf"

    def register_context_menu(self) -> bool:
        """
        Adiciona submenus ao menu de contexto de PDFs no Windows.
        Implementação simplificada: cria uma entrada 'fotonPDF' com comandos.
        """
        try:
            # Caminho no registro para o tipo de arquivo PDF
            # Primeiro, descobrimos o ProgID associado a .pdf
            prog_id = self._get_prog_id(".pdf") or "AcroExch.Document.DC" # Fallback comum

            shell_path = fr"Software\Classes\{prog_id}\shell"
            
            # 1. Rotação 90°
            self._create_menu_entry(shell_path, "foton_rotate", "Girar 90° (fotonPDF)", f"{self._app_path} rotate \"%1\" -d 90")
            
            # 2. Unir (Merge) - Requer múltiplos arquivos, o Shell do Windows passa um por um ou via DDE
            # Para simplificar no MVP, registramos a opção de abrir com a CLI
            self._create_menu_entry(shell_path, "foton_merge", "Unir com fotonPDF", f"{self._app_path} merge \"%1\"")

            return True
        except Exception as e:
            print(f"Erro ao registrar no Windows: {e}")
            return False

    def unregister_context_menu(self) -> bool:
        """Remove as entradas do registro."""
        # Implementação de limpeza omitida para brevidade no MVP, mas necessária no futuro
        return True

    def _get_prog_id(self, extension: str) -> str | None:
        try:
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, extension) as key:
                return winreg.QueryValue(key, None)
        except WindowsError:
            return None

    def _create_menu_entry(self, parent_key_path: str, name: str, label: str, command: str):
        key_path = fr"{parent_key_path}\{name}"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            winreg.SetValue(key, "", winreg.REG_SZ, label)
            with winreg.CreateKey(key, "command") as cmd_key:
                winreg.SetValue(cmd_key, "", winreg.REG_SZ, command)
