"""
FotonPDF Application Entry Point
================================
Fully resilient startup with comprehensive error tracing.
All failures are logged to a file for debugging.
"""
import sys
import os
import traceback
from datetime import datetime

# --- STARTUP LOG SYSTEM ---
# This runs BEFORE any imports to catch everything
STARTUP_LOG_PATH = os.path.join(os.environ.get('TEMP', '.'), 'fotonpdf_startup.log')

def startup_log(msg: str):
    """Write to startup log file immediately."""
    try:
        with open(STARTUP_LOG_PATH, 'a', encoding='utf-8') as f:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            f.write(f"[{timestamp}] {msg}\n")
            f.flush()
    except:
        pass  # Silent fail for logging itself

# Clear old log on fresh start
try:
    with open(STARTUP_LOG_PATH, 'w', encoding='utf-8') as f:
        f.write(f"=== FotonPDF Startup Log ===\n")
        f.write(f"Started at: {datetime.now().isoformat()}\n")
        f.write(f"Python: {sys.version}\n")
        f.write(f"Execpath: {sys.executable}\n\n")
except:
    pass

startup_log("Stage 0: Startup log initialized")

# --- IMPORT STAGE 1: Core Python ---
try:
    startup_log("Stage 1: Importing core Python modules...")
    from pathlib import Path
    import ctypes
    startup_log("Stage 1: OK")
except Exception as e:
    startup_log(f"Stage 1 FAILED: {e}\n{traceback.format_exc()}")
    sys.exit(1)

# --- IMPORT STAGE 2: PyQt6 Core ---
try:
    startup_log("Stage 2: Importing PyQt6...")
    from PyQt6.QtWidgets import QApplication, QMessageBox
    from PyQt6.QtCore import qInstallMessageHandler, QtMsgType
    startup_log("Stage 2: OK")
except Exception as e:
    startup_log(f"Stage 2 FAILED (PyQt6): {e}\n{traceback.format_exc()}")
    print(f"CRITICAL: PyQt6 não pode ser importado: {e}", file=sys.stderr)
    sys.exit(1)

# --- QT MESSAGE HANDLER ---
# Capture ALL Qt debug/warning/error messages
def qt_message_handler(mode, context, message):
    """Capture Qt internal messages."""
    mode_str = {
        QtMsgType.QtDebugMsg: "DEBUG",
        QtMsgType.QtInfoMsg: "INFO", 
        QtMsgType.QtWarningMsg: "WARNING",
        QtMsgType.QtCriticalMsg: "CRITICAL",
        QtMsgType.QtFatalMsg: "FATAL"
    }.get(mode, "UNKNOWN")
    startup_log(f"Qt[{mode_str}]: {message}")
    # For fatal errors, also print to stderr
    if mode in (QtMsgType.QtCriticalMsg, QtMsgType.QtFatalMsg):
        print(f"Qt {mode_str}: {message}", file=sys.stderr)

qInstallMessageHandler(qt_message_handler)
startup_log("Qt message handler installed")

# --- EXCEPTION HOOK ---
def exception_hook(exctype, value, tb):
    """Global exception hook - logs everything."""
    msg = ''.join(traceback.format_exception(exctype, value, tb))
    startup_log(f"UNHANDLED EXCEPTION:\n{msg}")
    # Try to log via logger service if available
    try:
        from src.infrastructure.services.logger import log_exception
        log_exception(f"Unhandled: {exctype.__name__}: {value}")
    except:
        pass
    sys.__excepthook__(exctype, value, tb)

sys.excepthook = exception_hook
startup_log("Exception hook installed")

# --- IMPORT STAGE 3: MainWindow ---
MainWindow = None
try:
    startup_log("Stage 3: Importing MainWindow...")
    from src.interfaces.gui.main_window import MainWindow
    startup_log("Stage 3: OK")
except Exception as e:
    startup_log(f"Stage 3 FAILED (MainWindow import): {e}\n{traceback.format_exc()}")
    MainWindow = None  # Will create fallback

def hide_console():
    """Hide console window on Windows."""
    if sys.platform == "win32":
        try:
            kernel32 = ctypes.WinDLL('kernel32')
            user32 = ctypes.WinDLL('user32')
            hWnd = kernel32.GetConsoleWindow()
            if hWnd:
                user32.ShowWindow(hWnd, 0)
        except:
            pass

def show_error_dialog(app, title: str, message: str, details: str = None):
    """Show error dialog to user."""
    try:
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        if details:
            msg_box.setDetailedText(details)
        msg_box.setInformativeText(f"Log salvo em: {STARTUP_LOG_PATH}")
        msg_box.exec()
    except:
        print(f"CRITICAL: {message}\n{details}", file=sys.stderr)

def create_fallback_window():
    """Create minimal fallback window when MainWindow fails."""
    from PyQt6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton
    from PyQt6.QtCore import Qt
    
    class FallbackWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("fotonPDF - Erro de Inicialização")
            self.setMinimumSize(600, 400)
            
            central = QWidget()
            self.setCentralWidget(central)
            layout = QVBoxLayout(central)
            
            # Error message
            error_label = QLabel("⚠️ O FotonPDF não pôde iniciar completamente.")
            error_label.setStyleSheet("font-size: 18px; color: #ff6b6b;")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(error_label)
            
            # Instructions
            info_label = QLabel(f"Verifique o log em:\n{STARTUP_LOG_PATH}")
            info_label.setStyleSheet("font-size: 14px; color: #999;")
            info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(info_label)
            
            # Open log button
            btn = QPushButton("Abrir Log de Startup")
            btn.clicked.connect(lambda: os.startfile(STARTUP_LOG_PATH) if sys.platform == 'win32' else None)
            layout.addWidget(btn)
            
            self.setStyleSheet("background-color: #1e1e2e;")
    
    return FallbackWindow()

def main(file_path: str = None):
    startup_log("Entering main()")
    
    # Hide console (optional for release builds)
    # hide_console()
    
    try:
        startup_log("Creating QApplication...")
        app = QApplication(sys.argv)
        app.setApplicationName("fotonPDF")
        startup_log("QApplication created successfully")
        
        # Check if MainWindow imported successfully
        if MainWindow is None:
            startup_log("MainWindow failed to import, using fallback")
            window = create_fallback_window()
        else:
            try:
                startup_log("Creating MainWindow instance...")
                initial_file = Path(file_path) if file_path else None
                
                # Injeção de dependência via conector hexagonal
                from src.infrastructure.adapters.gui_settings_adapter import GUISettingsAdapter
                settings_connector = GUISettingsAdapter()
                
                window = MainWindow(initial_file=initial_file, settings_connector=settings_connector)
                startup_log("MainWindow created successfully")
            except Exception as e:
                startup_log(f"MainWindow.__init__ FAILED: {e}\n{traceback.format_exc()}")
                show_error_dialog(
                    app, 
                    "Erro de Inicialização",
                    "Não foi possível criar a janela principal.",
                    traceback.format_exc()
                )
                window = create_fallback_window()
        
        startup_log("Showing window...")
        window.show()
        startup_log("Window shown. Entering event loop...")
        
        exit_code = app.exec()
        startup_log(f"Event loop exited with code: {exit_code}")
        sys.exit(exit_code)
        
    except Exception as e:
        startup_log(f"CRITICAL main() EXCEPTION: {e}\n{traceback.format_exc()}")
        print(f"CRITICAL: {e}", file=sys.stderr)
        try:
            app = QApplication.instance()
            if app:
                show_error_dialog(app, "Erro Fatal", str(e), traceback.format_exc())
        except:
            pass
        sys.exit(1)

if __name__ == "__main__":
    arg_file = sys.argv[1] if len(sys.argv) > 1 else None
    main(arg_file)
