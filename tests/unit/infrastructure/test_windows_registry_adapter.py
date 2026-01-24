import pytest
import winreg
from unittest.mock import MagicMock, patch
from pathlib import Path
from src.infrastructure.adapters.windows_registry_adapter import WindowsRegistryAdapter

class MockRegistry:
    def __init__(self):
        self.keys = {}
        self.HKEY_CURRENT_USER = 1
        self.HKEY_CLASSES_ROOT = 2
        self.HKEY_LOCAL_MACHINE = 3
        self.hkey_map = {1: "HKCU", 2: "HKCR", 3: "HKLM"}
        self.REG_SZ = 1
        self.KEY_ALL_ACCESS = 983103
        self.KEY_READ = 131097
        self.KEY_SET_VALUE = 2

    def OpenKey(self, hkey, path, reserved=0, access=0):
        hkey_str = self.hkey_map.get(hkey, str(hkey)) if isinstance(hkey, int) else getattr(hkey, 'path', str(hkey))
        full_path = f"{hkey_str}\\{path}" if hkey_str else path
        if full_path not in self.keys:
            raise OSError(f"Key not found: {full_path}")
        mock_key = MagicMock()
        mock_key.path = full_path
        mock_key.__enter__.return_value = mock_key
        return mock_key

    def CreateKey(self, hkey, path):
        hkey_str = self.hkey_map.get(hkey, str(hkey)) if isinstance(hkey, int) else getattr(hkey, 'path', str(hkey))
        full_path = f"{hkey_str}\\{path}" if hkey_str else path
        if full_path not in self.keys:
            self.keys[full_path] = {"values": {}, "subkeys": []}
            # Update parent subkeys
            parts = full_path.split("\\")
            if len(parts) > 1:
                parent = "\\".join(parts[:-1])
                name = parts[-1]
                if parent in self.keys:
                    if name not in self.keys[parent]["subkeys"]:
                        self.keys[parent]["subkeys"].append(name)
        
        mock_key = MagicMock()
        mock_key.path = full_path
        mock_key.__enter__.return_value = mock_key
        return mock_key

    def SetValue(self, key, subkey, type, value):
        path = key.path
        if subkey:
            path = f"{path}\\{subkey}"
        if path not in self.keys:
            self.keys[path] = {"values": {}, "subkeys": []}
        self.keys[path]["values"][""] = value

    def SetValueEx(self, key, name, reserved, type, value):
        self.keys[key.path]["values"][name] = value

    def QueryValue(self, key, subkey):
        path = key.path
        if subkey:
            path = f"{path}\\{subkey}"
        return self.keys[path]["values"].get("", None)

    def EnumKey(self, key, index):
        subkeys = self.keys[key.path]["subkeys"]
        if index >= len(subkeys):
            raise OSError("No more keys")
        return subkeys[index]

    def DeleteKey(self, hkey, path):
        hkey_str = self.hkey_map.get(hkey, str(hkey)) if isinstance(hkey, int) else getattr(hkey, 'path', str(hkey))
        full_path = f"{hkey_str}\\{path}" if hkey_str else path
        if full_path in self.keys:
            del self.keys[full_path]
            # Remove from parent subkeys
            parts = full_path.split("\\")
            if len(parts) > 1:
                parent = "\\".join(parts[:-1])
                name = parts[-1]
                if parent in self.keys:
                    self.keys[parent]["subkeys"].remove(name)

@pytest.fixture
def mock_winreg():
    return MockRegistry()

@pytest.fixture
def adapter(mock_winreg):
    return WindowsRegistryAdapter(registry=mock_winreg)

def test_register_context_menu(adapter, mock_winreg):
    # Setup parent key
    mock_winreg.CreateKey("HKCU", r"Software\Classes\SystemFileAssociations\.pdf\shell")
    
    success = adapter.register_context_menu("Abrir no foton", "foton.exe %1")
    assert success
    
    expected_key = r"HKCU\Software\Classes\SystemFileAssociations\.pdf\shell\foton_Abrirnofoton"
    assert expected_key in mock_winreg.keys
    assert mock_winreg.keys[expected_key]["values"][""] == "Abrir no foton"
    assert mock_winreg.keys[f"{expected_key}\\command"]["values"][""] == "foton.exe %1"

def test_unregister_context_menu(adapter, mock_winreg):
    shell_path = r"Software\Classes\SystemFileAssociations\.pdf\shell"
    mock_winreg.CreateKey("HKCU", shell_path)
    mock_winreg.CreateKey("HKCU", f"{shell_path}\\foton_test")
    mock_winreg.CreateKey("HKCU", f"{shell_path}\\foton_test\\command")
    
    success = adapter.unregister_context_menu()
    assert success
    assert f"HKCU\\{shell_path}\\foton_test" not in mock_winreg.keys

def test_check_installation_status(adapter, mock_winreg):
    shell_path = r"Software\Classes\SystemFileAssociations\.pdf\shell"
    mock_winreg.CreateKey("HKCU", shell_path)
    
    assert adapter.check_installation_status() is False
    
    mock_winreg.CreateKey("HKCU", f"{shell_path}\\foton_app")
    assert adapter.check_installation_status() is True

def test_register_all_context_menus(adapter, mock_winreg):
    mock_winreg.CreateKey("HKCU", r"Software\Classes\SystemFileAssociations\.pdf\shell")
    
    with patch("src.infrastructure.services.resource_service.ResourceService.get_logo_ico", return_value="logo.ico"), \
         patch("src.infrastructure.adapters.windows_registry_adapter.log_error") as mock_log:
        success = adapter.register_all_context_menus()
        if not success:
            print(f"FAILED with error: {mock_log.call_args}")
        assert success
        
        # Check one of the keys
        expected_key = r"HKCU\Software\Classes\SystemFileAssociations\.pdf\shell\foton_01_Abrir"
        assert expected_key in mock_winreg.keys
        assert mock_winreg.keys[expected_key]["values"]["Icon"] == "logo.ico"

def test_set_as_default_viewer(adapter, mock_winreg):
    mock_winreg.CreateKey("HKCU", r"Software\RegisteredApplications")
    
    with patch("src.infrastructure.services.resource_service.ResourceService.get_logo_ico", return_value="logo.ico"), \
         patch("subprocess.run") as mock_run, \
         patch("src.infrastructure.adapters.windows_registry_adapter.log_error") as mock_log:
        success = adapter.set_as_default_viewer()
        if not success:
            print(f"FAILED with error: {mock_log.call_args}")
        assert success
        
        prog_id_key = r"HKCU\Software\Classes\fotonPDF.AssocFile.pdf"
        assert prog_id_key in mock_winreg.keys
        assert mock_winreg.keys[r"HKCU\Software\RegisteredApplications"]["values"]["fotonPDF"] == r"Software\fotonPDF\Capabilities"
