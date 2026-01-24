import sys
import subprocess
import time
import argparse
from pathlib import Path

# Tentar importar watchdog, instalar se necessário
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    print("⚠️  Biblioteca 'watchdog' não encontrada. Instalando...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "watchdog"])
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler

class ReloadHandler(FileSystemEventHandler):
    """
    Handler para monitorar mudanças e reiniciar o app.
    Foca em arquivos .py, .qss e .json.
    """
    def __init__(self, command):
        self.command = command
        self.process = None
        self.last_reload = 0
        self.start_app() # Inicia imediatamente

    def start_app(self):
        if self.process:
            print("🔄 Reiniciando fotonPDF...")
            self.process.terminate()
            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()
        
        # Inicia o processo
        self.process = subprocess.Popen(self.command, shell=True)

    def on_modified(self, event):
        if event.is_directory:
            return
        
        # Ignorar diretórios que não devem disparar reload (prevenção de loop)
        ignored_patterns = ["docs", ".git", "__pycache__", "build", "dist", ".obsidian", ".pytest_cache"]
        if any(pattern in event.src_path for pattern in ignored_patterns):
            return

        # Debounce de 1 segundo
        current_time = time.time()
        if current_time - self.last_reload < 1.0:
            return

        if event.src_path.endswith((".py", ".qss", ".json")):
            print(f"📂 Mudança detectada: {Path(event.src_path).name}")
            self.last_reload = current_time
            self.start_app()

def start_dev_session(mode: str):
    """
    Inicia a sessão de desenvolvimento com auto-reload.
    """
    project_root = Path(__file__).parent.parent.resolve()
    
    if mode == "mock":
        command = f'python "{project_root / "scripts" / "dev_gui_view.py"}"'
        path_to_watch = project_root
        print("🎨 Modo: MOCKUP VIEW (Real-time Design)")
    else:
        command = f'python -m src.interfaces.gui.app'
        path_to_watch = project_root / "src"
        print("🚀 Modo: PRODUCTION APP (Live Coding)")

    print(f"👀 Monitorando: {path_to_watch}")
    print(f"🎬 Executando: {command}\n")
    
    event_handler = ReloadHandler(command)
    observer = Observer()
    observer.schedule(event_handler, str(path_to_watch), recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Finalizando sessão de desenvolvimento...")
        observer.stop()
        if event_handler.process:
            event_handler.process.terminate()
    observer.join()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="fotonPDF Hot-Reload Development Tool")
    parser.add_argument(
        "--mode", 
        choices=["app", "mock"], 
        default="mock", 
        help="Modo de execução: 'app' para aplicação real, 'mock' para visão de design com dados fakes (default)."
    )
    args = parser.parse_args()
    
    start_dev_session(args.mode)
