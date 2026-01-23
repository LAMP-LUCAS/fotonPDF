import sys
from pathlib import Path
import ctypes
from PyQt6.QtWidgets import QApplication
from src.interfaces.gui.main_window import MainWindow

def hide_console():
    """Esconde a janela do console no Windows."""
    if sys.platform == "win32":
        kernel32 = ctypes.WinDLL('kernel32')
        user32 = ctypes.WinDLL('user32')
        hWnd = kernel32.GetConsoleWindow()
        if hWnd:
            user32.ShowWindow(hWnd, 0) # 0 = SW_HIDE

def exception_hook(exctype, value, traceback):
    """Gancho global para capturar exceções não tratadas e evitar fechamento abrupto."""
    from src.infrastructure.services.logger import log_exception
    log_exception(f"Unhandled Exception: {exctype}, {value}")
    sys.__excepthook__(exctype, value, traceback)

def main(file_path: str = None):
    # Definir gancho de exceção
    sys.excepthook = exception_hook
    
    # Esconder terminal se estivermos no visualizador
    hide_console()
    
    app = QApplication(sys.argv)
    app.setApplicationName("fotonPDF")
    
    # Converter string para Path se existir
    initial_file = Path(file_path) if file_path else None
    
    window = MainWindow(initial_file=initial_file)
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
