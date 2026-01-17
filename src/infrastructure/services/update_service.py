import requests
from pathlib import Path
from PyQt6.QtCore import QThread, pyqtSignal

class UpdateWorker(QThread):
    """Worker assíncrono para verificar atualizações no GitHub."""
    update_available = pyqtSignal(str, str)  # version, download_url
    error = pyqtSignal(str)

    def __init__(self, current_version: str, repo_url: str):
        super().__init__()
        self.current_version = current_version
        self.repo_url = repo_url # Ex: "LAMP-LUCAS/fotonPDF"

    def run(self):
        try:
            api_url = f"https://api.github.com/repos/{self.repo_url}/releases/latest"
            response = requests.get(api_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                latest_version = data.get("tag_name", "").strip("v")
                download_url = data.get("html_url")
                
                if latest_version > self.current_version:
                    self.update_available.emit(latest_version, download_url)
            elif response.status_code == 404:
                # Repositório ou release não encontrado
                pass
        except Exception as e:
            self.error.emit(str(e))

class UpdateService:
    """Serviço de orquestração de atualizações."""
    VERSION = "1.0.0" # Versão base inicial
    REPO = "LAMP-LUCAS/fotonPDF"

    def __init__(self):
        self.worker = None

    def check_for_updates(self, callback_success, callback_error=None):
        self.worker = UpdateWorker(self.VERSION, self.REPO)
        self.worker.update_available.connect(callback_success)
        if callback_error:
            self.worker.error.connect(callback_error)
        self.worker.start()
