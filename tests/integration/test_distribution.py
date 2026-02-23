import sys
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.infrastructure.adapters.windows_registry_adapter import WindowsRegistryAdapter

def test_registry_adapter_paths_in_dev_mode():
    """Garante que em modo DEV, _gui_path e _cli_path apontem para python main.py"""
    with patch("sys.frozen", False, create=True):
        adapter = WindowsRegistryAdapter()
        assert "python" in adapter._gui_path
        assert "main.py" in adapter._gui_path
        
        # Em Dev, ambos são iguais
        assert adapter._cli_path == adapter._gui_path

def test_registry_adapter_paths_in_frozen_mode():
    """Garante que em modo PRODUÇÃO, _gui_path aponte para .exe e _cli_path para -cli.exe"""
    fake_exe_path = r"C:\fake\app\foton.exe"
    with patch("sys.frozen", True, create=True), patch("sys.executable", fake_exe_path):
        adapter = WindowsRegistryAdapter()
        
        assert adapter._gui_path == r"C:\fake\app\foton.exe"
        assert adapter._cli_path == r"C:\fake\app\foton-cli.exe"

def test_register_context_menus_uses_correct_executables():
    """
    Garante que menus de ação chamam o foton-cli.exe (com console) e o
    menu 'Abrir' chama o foton.exe (GUI, sem console) e que usamos %V.
    """
    fake_exe_path = r"C:\fake\app\foton.exe"
    
    with patch("sys.frozen", True, create=True), \
         patch("sys._MEIPASS", r"C:\fake\meipass", create=True), \
         patch("sys.executable", fake_exe_path), \
         patch.object(WindowsRegistryAdapter, '_create_menu_entry') as mock_create:
        
        adapter = WindowsRegistryAdapter()
        adapter.register_all_context_menus()
        
        # Extrair quais comandos foram registrados para cada função
        found_abrir, found_girar, found_img = False, False, False
        
        
        for call in mock_create.call_args_list:
            # Puxamos todos os argumentos (args + kwargs) para fáceis "in" checks
            args_str = " ".join([str(a) for a in call.args]) + " ".join([str(v) for v in call.kwargs.values()])
            print(f"DEBUG: Args capturados no mock: {args_str}") # Add debug print
            
            if "Abrir" in args_str:
                assert "foton.exe" in args_str
                assert "foton-cli.exe" not in args_str
                assert '"%V"' in args_str
                found_abrir = True
            
            if "Girar 90" in args_str:
                assert "foton-cli.exe" in args_str
                assert '"%V"' in args_str
                found_girar = True
                
            if "Exportar Imagens" in args_str:
                assert "foton-cli.exe" in args_str
                assert "-f png" in args_str
                found_img = True
                
        assert found_abrir and found_girar and found_img, f"Nem todos os comandos foram registrados. Args vistos: {[c.args for c in mock_create.call_args_list]}"

def test_set_as_default_viewer_uses_gui_exe():
    """
    Garante que a associação padrão de duplo-clique (.pdf) aponte pro foton.exe (Sem abrir cmd.exe).
    """
    fake_exe_path = r"C:\fake\app\foton.exe"
    
    # Mockando _winreg pesadamente pois não queremos tocar no registro de verdade
    mock_winreg = MagicMock()
    
    adapter = WindowsRegistryAdapter(registry=mock_winreg)
    adapter._gui_path = r"C:\fake\app\foton.exe"
    
    with patch("subprocess.run"), \
         patch("sys.frozen", True, create=True), \
         patch("sys._MEIPASS", r"C:\fake\meipass", create=True), \
         patch("sys.executable", fake_exe_path):
        adapter.set_as_default_viewer()
    
    # Precisamos garantir que dalgum mock.SetValue chamou '"C:\...\foton.exe" view "%1"'
    # Já que assoc default via double-click do Windows joga %1 nativo em vez do click parsing da CLI
    found_correct_command = False
    for call in mock_winreg.SetValue.call_args_list:
        val = call.args[3] if len(call.args) > 3 else call.kwargs.get('value', '')
        if isinstance(val, str) and "foton.exe" in val and "view" in val:
            # Associação raiz de Windows OS manda %1 já clipado em aspas por double quote, %1 original mantido aqui
            assert '"%1"' in val 
            assert "foton-cli.exe" not in val
            found_correct_command = True
            
    assert found_correct_command, "Comando do Default Viewer não registrou o EXE GUI corretamente."
