import sys
import subprocess
import time
from pathlib import Path

def run_app():
    """Inicia o processo da aplicação principal."""
    cmd = [sys.executable, "-m", "src.interfaces.gui.app"]
    return subprocess.Popen(cmd)

def main():
    root_dir = Path(__file__).parent.parent.resolve()
    src_dir = root_dir / "src"
    
    print(f"🚀 Iniciando fotonPDF Dev Mode (Hot Reload)")
    print(f"📂 Monitorando: {src_dir}")
    print(f"💡 Dica: Salve qualquer arquivo em 'src/' para reiniciar o app.\n")

    current_process = run_app()
    
    # Dicionário para armazenar timestamps dos arquivos
    last_mtimes = {p: p.stat().st_mtime for p in src_dir.rglob("*.py")}

    try:
        while True:
            time.sleep(1) # Intervalo de polling
            changed = False
            
            # Verificar novos arquivos ou modificações
            for p in src_dir.rglob("*.py"):
                mtime = p.stat().st_mtime
                if p not in last_mtimes or mtime > last_mtimes[p]:
                    print(f"📝 Mudança detectada em: {p.name}")
                    last_mtimes[p] = mtime
                    changed = True
            
            if changed:
                print("♻️  Reiniciando aplicação...")
                current_process.terminate()
                try:
                    current_process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    current_process.kill()
                
                current_process = run_app()
                print("✅ Aplicação reiniciada.\n")

    except KeyboardInterrupt:
        print("\n🛑 Finalizando Dev Mode...")
        current_process.terminate()

if __name__ == "__main__":
    main()
