"""
Logger - Sistema de Logging do fotonPDF
Registra todas as operações em arquivo para diagnóstico.
"""
import logging
import sys
from pathlib import Path
from datetime import datetime


def get_log_path() -> Path:
    """Retorna o caminho do arquivo de log."""
    if getattr(sys, 'frozen', False):
        # Executável: log na mesma pasta do .exe
        base_path = Path(sys.executable).parent
    else:
        # Desenvolvimento: log na raíz do projeto
        base_path = Path(__file__).parents[3]
    
    log_dir = base_path / "logs"
    log_dir.mkdir(exist_ok=True)
    return log_dir / "fotonpdf.log"


def setup_logger() -> logging.Logger:
    """Configura e retorna o logger principal."""
    logger = logging.getLogger("fotonPDF")
    
    # Evitar duplicação de handlers
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.DEBUG)
    
    # Handler para arquivo
    log_path = get_log_path()
    file_handler = logging.FileHandler(log_path, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)
    
    # Handler para console (apenas erros)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)
    console_format = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    return logger


# Logger global
logger = setup_logger()


def log_info(message: str):
    """Registra mensagem informativa."""
    logger.info(message)


def log_warning(message: str):
    """Registra aviso."""
    logger.warning(message)


def log_error(message: str):
    """Registra erro."""
    logger.error(message)


def log_debug(message: str):
    """Registra mensagem de debug."""
    logger.debug(message)


def log_exception(message: str):
    """Registra exceção com traceback."""
    logger.exception(message)
