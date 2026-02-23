import sys
import subprocess
import time
import argparse
import socket
import threading
from pathlib import Path

# Tentar importar watchdog e psutil
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    import psutil
except ImportError:
    print("⚠️  Bibliotecas necessárias não encontradas. Instalando...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "watchdog", "psutil"])
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    import psutil

class ReloadHandler(FileSystemEventHandler):
    """
    Handler para monitorar mudanças e reiniciar o app com métricas de performance.
    """
    def __init__(self, command_args):
        self.command_args = command_args
        self.process = None
        self.last_reload = 0
        self.start_time = 0
        self._perf_thread = None
        self._stop_perf = False
        self.start_app() 

    def start_app(self):
        if self.process:
            print("\n🔄 Reiniciando fotonPDF...")
            self._stop_perf = True
            if self._perf_thread:
                self._perf_thread.join(timeout=1)
            
            # Matar processo e sua árvore (para ser robusto no Windows)
            try:
                parent = psutil.Process(self.process.pid)
                for child in parent.children(recursive=True):
                    child.terminate()
                parent.terminate()
            except:
                pass
        
        self.start_time = time.perf_counter()
        self._stop_perf = False
        self._last_heartbeat = time.time()
        
        # Iniciar servidor de heartbeat antes do app
        self._heartbeat_thread = threading.Thread(target=self._heartbeat_server, daemon=True)
        self._heartbeat_thread.start()
        
        # Injetar variáveis de ambiente para debug
        import os
        env = os.environ.copy()
        env["FOTON_DEBUG"] = "1"
        env["PYTHONUNBUFFERED"] = "1" # Garante logs em tempo real
        
        self.process = subprocess.Popen(self.command_args, env=env)
        
        # Iniciar thread de monitoramento de logs se em modo debug
        if os.environ.get("FOTON_DEBUG") == "1":
            log_path = project_root / "logs" / "fotonpdf.log"
            self._log_thread = threading.Thread(target=self._tail_logs, args=(log_path,), daemon=True)
            self._log_thread.start()
        
        # Iniciar thread de monitoramento de performance
        self._perf_thread = threading.Thread(target=self._monitor_performance, daemon=True)
        self._perf_thread.start()

    def _tail_logs(self, log_path: Path):
        """Monitora o arquivo de log e imprime novas linhas."""
        if not log_path.exists():
            # Aguarda o logger criar o arquivo
            time.sleep(2)
            if not log_path.exists(): return
            
        with open(log_path, "r", encoding="utf-8") as f:
            # Ir para o fim do arquivo
            f.seek(0, 2)
            while not self._stop_perf:
                line = f.readline()
                if not line:
                    time.sleep(0.1)
                    continue
                # Imprimir line removendo o newline extra se existir
                print(f"  \033[90m> {line.strip()}\033[0m")

    def _heartbeat_server(self):
        """Escuta pings UDP do app para detectar travamento da GUI."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('127.0.0.1', 9999))
        except Exception as e:
            print(f"⚠️  Não foi possível iniciar monitor de Heartbeat (Porta ocupada): {e}")
            return
        
        sock.settimeout(1.0)
        
        while not self._stop_perf:
            try:
                # O app envia apenas um byte '1'
                _, _ = sock.recvfrom(1)
                self._last_heartbeat = time.time()
            except socket.timeout:
                if time.time() - self._last_heartbeat > 2.0 and self.process and self.process.poll() is None:
                    print(f"\r⚠️  [GUI FREEZE DETECTED] A interface não responde há {time.time() - self._last_heartbeat:.1f}s   ", end="")
            except:
                break
        sock.close()

    def _monitor_performance(self):
        """Monitora RAM/CPU do processo em tempo real."""
        time.sleep(1.5) # Espera o app estabilizar
        startup_duration = time.perf_counter() - self.start_time
        print(f"⏱️  Tempo de carregamento: {startup_duration:.2f}s")
        
        try:
            proc = psutil.Process(self.process.pid)
            while not self._stop_perf and self.process.poll() is None:
                # Loop vazio ou informativo leve
                time.sleep(5)
        except:
            pass

    def on_modified(self, event):
        if event.is_directory:
            return
        
        ignored_patterns = ["docs", ".git", "__pycache__", "build", "dist", ".obsidian", ".pytest_cache", "logs"]
        if any(pattern in event.src_path for pattern in ignored_patterns):
            return

        current_time = time.time()
        if current_time - self.last_reload < 1.0:
            return

        if event.src_path.endswith((".py", ".qss", ".json")):
            print(f"\n📂 Mudança detectada: {Path(event.src_path).name}")
            self.last_reload = current_time
            self.start_app()

def start_dev_session(mode: str):
    """
    Inicia a sessão de desenvolvimento com auto-reload e performance metrics.
    """
    project_root = Path(__file__).parent.parent.resolve()
    python_exe = sys.executable
    
    if mode == "mock":
        command_args = [python_exe, str(project_root / "scripts" / "dev_gui_view.py")]
        path_to_watch = project_root
        print("🎨 Modo: MOCKUP VIEW (Real-time Design)")
    else:
        command_args = [python_exe, "-m", "src.interfaces.gui.app"]
        path_to_watch = project_root / "src"
        print("🚀 Modo: PRODUCTION APP (Live Coding)")

    print(f"👀 Monitorando: {path_to_watch}")
    print(f"🎬 Executando: {' '.join(command_args)}\n")
    
    event_handler = ReloadHandler(command_args)
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
