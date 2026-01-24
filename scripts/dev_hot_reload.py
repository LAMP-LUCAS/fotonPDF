import sys
import subprocess
import time
from pathlib import Path

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
    Foca em arquivos .py e .qss (se houver).
    """
    def __init__(self, command):
        self.command = command
        self.process = None
        self.last_reload = 0
        self.start_app()

    def start_app(self):
        if self.process:
            print("🔄 Reiniciando fotonPDF...")
            self.process.terminate()
            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()
        
        self.process = subprocess.Popen(self.command, shell=True)

    def on_modified(self, event):
        if event.is_directory:
            return
        
        # Debounce de 1 segundo para evitar reloads múltiplos em salvamentos rápidos
        current_time = time.time()
        if current_time - self.last_reload < 1.0:
            return

        if event.src_path.endswith((".py", ".qss", ".json")):
            print(f"📂 Mudança detectada: {Path(event.src_path).name}")
            self.last_reload = current_time
            self.start_app()

def start_dev_session():
    """
    Inicia a sessão de desenvolvimento com auto-reload.
    """
    path = "src"
    command = "python -m src.interfaces.gui.development_view"
    
    print("🚀 Iniciando FotonDev Hot-Reload Shell...")
    print(f"👀 Monitorando diretório: {path}")
    print(f"🎬 Executando: {command}")
    
    event_handler = ReloadHandler(command)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        if event_handler.process:
            event_handler.process.terminate()
    observer.join()

if __name__ == "__main__":
    start_dev_session()
