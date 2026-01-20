import sys
import winreg
import subprocess
from pathlib import Path
from src.domain.ports.os_integration import OSIntegrationPort
from src.infrastructure.services.logger import log_info, log_error, log_debug
from src.infrastructure.services.resource_service import ResourceService

# Caminho moderno para menu de contexto de PDFs (funciona independente do leitor instalado)
PDF_SHELL_PATH = r"Software\Classes\SystemFileAssociations\.pdf\shell"


class WindowsRegistryAdapter(OSIntegrationPort):
    """Adaptador para manipular o Registro do Windows e adicionar o Menu de Contexto."""

    def __init__(self):
        self._app_path = sys.executable if getattr(sys, 'frozen', False) else f'"{sys.executable}" "{Path(__file__).parents[2] / "interfaces" / "cli" / "main.py"}"'
        self._ext = ".pdf"

    def register_context_menu(self, label: str, command: str) -> bool:
        """
        Adiciona uma entrada ao menu de contexto de PDFs no Windows.
        Usa SystemFileAssociations que é o método moderno e mais confiável.
        """
        try:
            # Criar a entrada usando o caminho moderno
            clean_name = "".join(x for x in label if x.isalnum())
            entry_name = f"foton_{clean_name}"
            
            log_debug(f"Registrando em: HKCU\\{PDF_SHELL_PATH}\\{entry_name}")
            self._create_menu_entry(PDF_SHELL_PATH, entry_name, label, command)
            
            log_info(f"Menu de contexto registrado: {label}")
            return True
        except Exception as e:
            log_error(f"Erro ao registrar no Windows: {e}")
            return False

    def unregister_context_menu(self) -> bool:
        """Remove as entradas do registro que pertencem ao fotonPDF."""
        try:
            removed_count = 0
            
            # Tentar remover do caminho moderno
            removed_count += self._remove_foton_entries(PDF_SHELL_PATH)
            
            # Tentar remover do ProgID antigo também (limpeza)
            prog_id = self._get_prog_id(".pdf")
            if prog_id:
                old_path = fr"Software\Classes\{prog_id}\shell"
                removed_count += self._remove_foton_entries(old_path)
            
            # Fallback para AcroExch
            acro_path = r"Software\Classes\AcroExch.Document.DC\shell"
            removed_count += self._remove_foton_entries(acro_path)
            
            log_info(f"Entradas removidas: {removed_count}")
            return True
        except Exception as e:
            log_error(f"Erro ao remover do Windows: {e}")
            return False

    def _remove_foton_entries(self, shell_path: str) -> int:
        """Remove entradas foton_ de um caminho de shell específico."""
        removed = 0
        try:
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
                    cmd_path = fr"{shell_path}\{k}\command"
                    try:
                        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, cmd_path)
                    except OSError:
                        pass
                    try:
                        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, fr"{shell_path}\{k}")
                        removed += 1
                        log_debug(f"Removido: {k}")
                    except OSError:
                        pass
        except OSError:
            pass
        return removed

    def check_installation_status(self) -> bool:
        """Verifica se o fotonPDF está registrado no menu de contexto."""
        try:
            # Verificar no caminho moderno
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, PDF_SHELL_PATH, 0, winreg.KEY_READ) as key:
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

    def get_registered_command(self) -> str | None:
        """Retorna o comando registrado, se houver."""
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, PDF_SHELL_PATH, 0, winreg.KEY_READ) as key:
                i = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        if subkey_name.startswith("foton_"):
                            cmd_path = fr"{PDF_SHELL_PATH}\{subkey_name}\command"
                            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, cmd_path) as cmd_key:
                                return winreg.QueryValue(cmd_key, None)
                        i += 1
                    except OSError:
                        break
        except Exception:
            pass
        return None

    def _get_prog_id(self, extension: str) -> str | None:
        try:
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, extension) as key:
                value = winreg.QueryValue(key, None)
                return value if value else None
        except WindowsError:
            return None

    def _create_menu_entry(self, parent_key_path: str, name: str, label: str, command: str, icon_path: str = None):
        key_path = fr"{parent_key_path}\{name}"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            winreg.SetValue(key, "", winreg.REG_SZ, label)
            if icon_path:
                winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, icon_path)
            with winreg.CreateKey(key, "command") as cmd_key:
                winreg.SetValue(cmd_key, "", winreg.REG_SZ, command)

    def register_all_context_menus(self) -> bool:
        """
        Registra todas as entradas do menu de contexto para PDFs.
        Usa prefixo 'fotonPDF' para agrupamento visual.
        """
        try:
            # Detectar caminho do executável
            if getattr(sys, 'frozen', False):
                app_path = sys.executable
            else:
                # Modo desenvolvimento
                cli_path = Path(__file__).parents[2] / "interfaces" / "cli" / "main.py"
                app_path = f'python "{cli_path}"'
            
            # Menus organizados com prefixo para agrupamento visual
            menus = [
                ("foton_01_Abrir", "fotonPDF ▸ Abrir", f'"{app_path}" view "%1"'),
                ("foton_02_Girar90", "fotonPDF ▸ Girar 90°", f'"{app_path}" rotate "%1" -d 90'),
                ("foton_03_Girar180", "fotonPDF ▸ Girar 180°", f'"{app_path}" rotate "%1" -d 180'),
                ("foton_04_Girar270", "fotonPDF ▸ Girar 270°", f'"{app_path}" rotate "%1" -d 270'),
                ("foton_05_ExportMD", "fotonPDF ▸ Exportar Markdown", f'"{app_path}" export-md "%1"'),
                ("foton_06_ExportPNG", "fotonPDF ▸ Exportar Imagens (Todas)", f'"{app_path}" export-img "%1" -f png'),
            ]
            
            # Caminho do ícone oficial
            official_icon = str(ResourceService.get_logo_ico())
            
            for entry_name, label, command in menus:
                log_debug(f"Registrando: {label}")
                self._create_menu_entry(PDF_SHELL_PATH, entry_name, label, command, icon_path=official_icon)
            
            log_info(f"Registradas {len(menus)} entradas no menu de contexto")
            return True
            
        except Exception as e:
            log_error(f"Erro ao registrar menus: {e}")
            return False

    def repair_installation(self) -> bool:
        """
        Verifica se a instalação atual está correta e repara se necessário.
        Útil se o usuário mover a pasta do software ou se as chaves forem corrompidas.
        """
        try:
            log_info("Iniciando reparo da instalação...")
            
            # 1. Verificar se as chaves existem
            if not self.check_installation_status():
                log_warning("Instalação não encontrada. Criando nova...")
                return self.register_all_context_menus()
            
            # 2. Verificar se o comando apontado é o mesmo que o executável atual
            registered_cmd = self.get_registered_command()
            
            # Montar comando esperado para comparação
            if getattr(sys, 'frozen', False):
                current_exe = sys.executable
            else:
                cli_path = Path(__file__).parents[2] / "interfaces" / "cli" / "main.py"
                current_exe = f'python "{cli_path}"'
                
            expected_part = f'"{current_exe}"'
            
            if registered_cmd and expected_part not in registered_cmd:
                log_warning(f"Caminho no registro desatualizado. Atualizando para: {current_exe}")
                return self.register_all_context_menus()
            
            log_info("Instalação está íntegra e atualizada.")
            return True
        except Exception as e:
            log_error(f"Erro durante o reparo: {e}")
            return False

    def create_shortcut(self, location: str) -> bool:
        """Cria um atalho para o fotonPDF usando PowerShell."""
        try:
            if getattr(sys, 'frozen', False):
                target_path = sys.executable
            else:
                # No modo dev não faz muito sentido criar atalhos, mas vamos apontar para o main.py
                target_path = str(Path(__file__).parents[2] / "interfaces" / "cli" / "main.py")

            if location == "desktop":
                shortcut_path = "$([Environment]::GetFolderPath('Desktop'))"
            elif location == "start_menu":
                shortcut_path = "$([Environment]::GetFolderPath('StartMenu'))"
            else:
                return False

            icon_path = str(ResourceService.get_logo_ico())
            
            ps_script = f"""
            $WshShell = New-Object -ComObject WScript.Shell
            $Shortcut = $WshShell.CreateShortcut("{shortcut_path}\\fotonPDF.lnk")
            $Shortcut.TargetPath = "{target_path}"
            $Shortcut.Arguments = "view"
            $Shortcut.IconLocation = "{icon_path}"
            $Shortcut.Description = "Visualizador de PDFs Ultra-Rápido"
            $Shortcut.Save()
            """
            subprocess.run(["powershell", "-Command", ps_script], check=True, capture_output=True)
            log_info(f"Atalho criado em: {location}")
            return True
        except Exception as e:
            log_error(f"Erro ao criar atalho: {e}")
            return False

    def remove_shortcut(self, location: str) -> bool:
        """Remove o atalho do fotonPDF."""
        try:
            if location == "desktop":
                shortcut_path = "$([Environment]::GetFolderPath('Desktop'))"
            elif location == "start_menu":
                shortcut_path = "$([Environment]::GetFolderPath('StartMenu'))"
            else:
                return False

            ps_script = f"Remove-Item -Path '{shortcut_path}\\fotonPDF.lnk' -Force -ErrorAction SilentlyContinue"
            subprocess.run(["powershell", "-Command", ps_script], check=True, capture_output=True)
            log_info(f"Atalho removido de: {location}")
            return True
        except Exception as e:
            log_error(f"Erro ao remover atalho: {e}")
            return False

    def set_as_default_viewer(self) -> bool:
        """
        Associa o fotonPDF como o programa padrão para arquivos .pdf.
        Isso registra a capacidade; o Windows 10/11 pode pedir confirmação.
        """
        try:
            if getattr(sys, 'frozen', False):
                app_path = sys.executable
            else:
                app_path = f'python "{Path(__file__).parents[2] / "interfaces" / "cli" / "main.py"}"'

            prog_id = "fotonPDF.AssocFile.pdf"
            icon_path = str(ResourceService.get_logo_ico())

            # 1. Registrar o ProgID
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, fr"Software\Classes\{prog_id}") as key:
                winreg.SetValue(key, "", winreg.REG_SZ, "fotonPDF Document")
                with winreg.CreateKey(key, "DefaultIcon") as icon_key:
                    winreg.SetValue(icon_key, "", winreg.REG_SZ, icon_path)
                with winreg.CreateKey(key, r"shell\open\command") as cmd_key:
                    winreg.SetValue(cmd_key, "", winreg.REG_SZ, f'"{app_path}" view "%1"')

            # 2. Registrar a capacidade
            app_reg_path = r"Software\fotonPDF\Capabilities"
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, app_reg_path) as key:
                winreg.SetValue(key, "ApplicationDescription", winreg.REG_SZ, "Visualizador de PDFs ultra-rápido.")
                winreg.SetValue(key, "ApplicationName", winreg.REG_SZ, "fotonPDF")
                with winreg.CreateKey(key, "FileAssociations") as assoc_key:
                    winreg.SetValueEx(assoc_key, ".pdf", 0, winreg.REG_SZ, prog_id)

            # 3. Registrar o app para que apareça em "Abrir com" e "Programas Padrão"
            reg_apps_path = r"Software\RegisteredApplications"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_apps_path, 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, "fotonPDF", 0, winreg.REG_SZ, app_reg_path)

            # 4. Notificar o sistema sobre a mudança de associação (via PowerShell para SHChangeNotify)
            ps_notify = "[Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms'); [System.Windows.Forms.MethodInvoker]{ [void]([System.Runtime.InteropServices.Marshal]::GetComInterfaceForObject([New-Object -ComObject Shell.Application], [System.Runtime.InteropServices.Marshal]::GetType('System.Runtime.InteropServices.Marshal+ComInterface')).SHChangeNotify(0x08000000, 0, [IntPtr]::Zero, [IntPtr]::Zero)) }"
            # Ignoramos erros do notify pois é apenas cosmético
            subprocess.run(["powershell", "-Command", ps_notify], capture_output=True)

            log_info("Associação de arquivo .pdf registrada com sucesso.")
            return True
        except Exception as e:
            log_error(f"Erro ao definir programa padrão: {e}")
            return False
