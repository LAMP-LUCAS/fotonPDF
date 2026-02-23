import os
from datetime import datetime
from pathlib import Path

class StartupLogger:
    """
    Serviço dedicado para registrar o processo de inicialização e diagnóstico de boot.
    Substitui as funções inline _log_stage e _log_widget da MainWindow.
    """
    
    _log_path = os.path.join(os.environ.get('TEMP', '.'), 'fotonpdf_startup.log')

    @classmethod
    def log(cls, stage: str, error: Exception = None):
        """Registra uma etapa de inicialização."""
        try:
            with open(cls._log_path, 'a', encoding='utf-8') as f:
                timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
                if error:
                    f.write(f"[{timestamp}] {stage} FAILED: {error}\n")
                else:
                    f.write(f"[{timestamp}] {stage} OK\n")
        except:
            # Falha silenciosa no logger de diagnóstico é intencional para não travar o boot
            pass

    @classmethod
    def clear(cls):
        """Limpa o log de inicialização anterior."""
        try:
            if os.path.exists(cls._log_path):
                os.remove(cls._log_path)
        except:
            pass
