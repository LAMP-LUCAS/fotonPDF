import sys
import winreg
from pathlib import Path
from src.domain.ports.os_integration import OSIntegrationPort

class WindowsRegistryAdapter(OSIntegrationPort):
    """Adaptador para manipular o Registro do Windows e adicionar o Menu de Contexto."""

    def __init__(self):
        self._app_path = sys.executable if getattr(sys, 'frozen', False) else f'"{sys.executable}" "{Path(__file__).parents[2] / "interfaces" / "cli" / "main.py"}"'
        self._ext = ".pdf"

    def register_context_menu(self, label: str, command: str) -> bool:
        """
        Adiciona uma entrada ao menu de contexto de PDFs no Windows.
        """
        try:
            # Descobrimos o ProgID associado a .pdf
            prog_id = self._get_prog_id(".pdf") or "AcroExch.Document.DC"
            shell_path = fr"Software\Classes\{prog_id}\shell"
            
            # Criar a entrada principal pedida (ex: "Abrir com fotonPDF")
            clean_name = "".join(x for x in label if x.isalnum())
            self._create_menu_entry(shell_path, f"foton_{clean_name}", label, command)
            
            return True
        except Exception as e:
            print(f"Erro ao registrar no Windows: {e}")
            return False

    def unregister_context_menu(self) -> bool:
        """Remove as entradas do registro que pertencem ao fotonPDF."""
        try:
            prog_id = self._get_prog_id(".pdf") or "AcroExch.Document.DC"
            shell_path = fr"Software\Classes\{prog_id}\shell"
            
            # Precisamos iterar pelas chaves e remover as que começam com 'foton_'
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, shell_path, 0, winreg.KEY_ALL_ACCESS) as key:
                i = 0
                keys_to_delete = []
                while True:
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        if subkey_name.startswith("foton_"):
                            keys_to_delete.append(subkey_name)
                        i += 1
                    except OSError:
                        break
                
                for k in keys_to_delete:
                    # winreg.DeleteKey não remove recursivamente chaves com subchaves (como 'command')
                    # Precisamos remover o 'command' primeiro
                    cmd_path = fr"{shell_path}\{k}\command"
                    try:
                        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, cmd_path)
                    except OSError:
                        pass
                    winreg.DeleteKey(winreg.HKEY_CURRENT_USER, fr"{shell_path}\{k}")
                    
            return True
        except Exception as e:
            print(f"Erro ao remover do Windows: {e}")
            return False

    def check_installation_status(self) -> bool:
        """Verifica se o fotonPDF está registrado no menu de contexto."""
        try:
            prog_id = self._get_prog_id(".pdf") or "AcroExch.Document.DC"
            shell_path = fr"Software\Classes\{prog_id}\shell"
            
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, shell_path, 0, winreg.KEY_READ) as key:
                i = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        if subkey_name.startswith("foton_"):
                            return True
                        i += 1
                    except OSError:
                        break
            return False
        except Exception:
            return False

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
