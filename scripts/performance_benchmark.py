import os
import sys
import time
import psutil
from pathlib import Path

# Adicionar src ao path para importar componentes
sys.path.append(str(Path(__file__).parents[1]))

def measure_startup():
    print("🚀 Iniciando benchmark de inicialização (Cold Start)...")
    
    start_time = time.perf_counter()
    
    # Simular o carregamento das dependências pesadas
    import PyQt6.QtWidgets as QtWidgets
    import fitz
    from src.interfaces.gui.app import main
    dependencies_time = time.perf_counter()
    
    print(f"  - Importação de dependências: {dependencies_time - start_time:.4f}s")
    
    # Para medir o tempo total até o show() sem bloquear o script, 
    # precisaríamos de um hook no MainWindow.
    # Como não queremos abrir a GUI real agora, vamos medir a criação dos objetos principais.
    from src.interfaces.gui.main_window import MainWindow
    from src.infrastructure.adapters.gui_settings_adapter import GUISettingsAdapter
    
    init_start = time.perf_counter()
    app = QtWidgets.QApplication(sys.argv) # Inicializar app
    _ = MainWindow(settings_connector=GUISettingsAdapter())
    init_end = time.perf_counter()
    
    print(f"  - Inicialização da MainWindow: {init_end - init_start:.4f}s")
    print(f"✅ Tempo Total Estimado: {init_end - start_time:.4f}s")

def measure_hardware_usage():
    print("\n📊 Medindo consumo de hardware...")
    
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    
    print(f"  - Memória RAM (RSS): {mem_info.rss / 1024 / 1024:.2f} MB")
    print(f"  - Memória Virtual (VMS): {mem_info.vms / 1024 / 1024:.2f} MB")
    print(f"  - Threads Ativas: {process.num_threads()}")
    
    # Medir CPU curta duração
    cpu_usage = process.cpu_percent(interval=0.5)
    print(f"  - Uso de CPU (Basal): {cpu_usage}%")

def measure_pdf_loading(pdf_path: str):
    if not os.path.exists(pdf_path):
        print(f"\n⚠️ Arquivo para teste não encontrado: {pdf_path}")
        return

    print(f"\n📑 Medindo performance de carregamento de PDF: {os.path.basename(pdf_path)}")
    
    from src.infrastructure.services.telemetry_service import TelemetryService
    
    p = Path(pdf_path)
    start = time.perf_counter()
    import fitz
    doc = fitz.open(pdf_path)
    # Simular metadados (o que o app faz)
    _ = doc.page_count
    _ = doc.get_toc()
    open_time = time.perf_counter() - start
    
    # Registrar no histórico central
    TelemetryService.log_operation("BENCHMARK_OPEN", p, open_time)
    
    print(f"  - Abertura Total: {open_time:.4f}s")
    print(f"  - Total de Páginas: {len(doc)}")
    
    # Medir renderização da primeira página
    page = doc[0]
    render_start = time.perf_counter()
    _ = page.get_pixmap()
    render_end = time.perf_counter()
    
    TelemetryService.log_operation("BENCHMARK_RENDER_P1", p, render_end - render_start)
    
    print(f"  - Renderização Pág 1: {render_end - render_start:.4f}s")
    doc.close()

if __name__ == "__main__":
    # Garantir que pasta de logs existe
    os.makedirs("logs", exist_ok=True)
    
    # Capturar output para arquivo
    class Logger(object):
        def __init__(self):
            self.terminal = sys.stdout
            self.log = open("logs/performance_report.txt", "w", encoding="utf-8")
        def write(self, message):
            self.terminal.write(message)
            self.log.write(message)
        def flush(self):
            pass

    sys.stdout = Logger()

    measure_startup()
    measure_hardware_usage()
    
    # Tentar com um arquivo PDF existente no repo
    test_pdf = os.path.join(os.path.dirname(__file__), "..", "manual_test.pdf")
    measure_pdf_loading(test_pdf)
    
    print(f"\n✨ Benchmark concluído em {time.strftime('%Y-%m-%d %H:%M:%S')}")
