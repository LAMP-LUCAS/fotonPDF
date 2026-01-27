import os
import time
import psutil
import csv
import sys
from pathlib import Path
from datetime import datetime
from src.infrastructure.services.logger import log_debug

class TelemetryService:
    """
    Serviço de monitoramento de performance e telemetria de hardware.
    Registra métricas detalhadas sobre operações pesadas (abertura de PDF, OCR, etc).
    """
    
    _header_written = False
    _start_times = {} # Para medir TTU (Time to Usability)

    @staticmethod
    def get_log_path() -> Path:
        """Define o caminho para o arquivo de histórico de performance."""
        try:
            if getattr(sys, 'frozen', False):
                base_path = Path(sys.executable).parent
            else:
                # src/infrastructure/services/telemetry_service.py -> src/infrastructure/services -> src/infrastructure -> src -> root
                base_path = Path(__file__).parents[3]
            
            log_dir = base_path / "logs"
            log_dir.mkdir(exist_ok=True)
            return log_dir / "performance_history.csv"
        except Exception:
            return Path("performance_history.csv")

    @classmethod
    def mark_start(cls, operation: str):
        """Marca o início de uma operação para cálculo de TTU."""
        cls._start_times[operation] = time.perf_counter()

    @classmethod
    def log_operation(cls, operation: str, file_path: Path | None = None, duration: float = 0.0):
        """
        Registra uma operação no histórico.
        Se 'duration' for 0, tenta calcular usando mark_start prévio.
        """
        if duration == 0 and operation in cls._start_times:
            duration = time.perf_counter() - cls._start_times.pop(operation)
            
        log_path = cls.get_log_path()
        write_header = not log_path.exists()
        
        try:
            # Coletar estatísticas do arquivo
            file_size_mb = 0.0
            file_name = "N/A"
            if file_path and file_path.exists():
                file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
                file_name = file_path.name

            # Coletar métricas do processo atual (mais rápido que recursivo)
            process = psutil.Process(os.getpid())
            mem_rss_mb = process.memory_info().rss / (1024 * 1024)
            cpu_usage = process.cpu_percent(interval=None)
            
            row = [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                operation,
                file_name,
                f"{file_size_mb:.2f}",
                f"{duration:.4f}",
                f"{mem_rss_mb:.2f}",
                f"{cpu_usage:.1f}",
                process.num_threads()
            ]

            # Gravação rápida
            with open(log_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if write_header:
                    writer.writerow([
                        "Timestamp", "Operação", "Arquivo", "Tamanho_MB", 
                        "Duração_Seg", "RAM__MB", "CPU_Percent", "Threads"
                    ])
                writer.writerow(row)
            
            log_debug(f"Telemetry: {operation} - {file_name} took {duration:.4f}s")
            
        except Exception:
            pass # Silencioso para não travar o app
