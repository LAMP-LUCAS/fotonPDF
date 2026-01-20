import requests
from src import __version__
from src.infrastructure.services.logger import log_info, log_error, log_debug

GITHUB_REPO = "LAMP-LUCAS/fotonPDF"
API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"

class UpdateService:
    """Serviço para verificar atualizações no GitHub."""

    def check_for_updates(self) -> dict | None:
        """
        Verifica se há uma versão mais recente disponível.
        Retorna um dicionário com info da release ou None se já estiver atualizado.
        """
        try:
            log_debug(f"Verificando atualizações em: {API_URL}")
            response = requests.get(API_URL, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                latest_version = data.get("tag_name", "").replace("v", "")
                
                if self._is_newer(latest_version, __version__):
                    log_info(f"Nova versão encontrada: {latest_version} (atual: {__version__})")
                    return {
                        "version": latest_version,
                        "url": data.get("html_url"),
                        "body": data.get("body")
                    }
                else:
                    log_debug("Sistema já está na versão mais recente.")
            elif response.status_code == 404:
                log_debug("Nenhuma release encontrada no repositório.")
            else:
                log_error(f"Erro ao verificar atualizações: Status {response.status_code}")
                
        except Exception as e:
            log_error(f"Erro na conexão com GitHub: {e}")
            
        return None

    def _is_newer(self, latest: str, current: str) -> bool:
        """Compara duas strings de versão simples (ex: 1.0.0)."""
        try:
            l_parts = [int(p) for p in latest.split(".")]
            c_parts = [int(p) for p in current.split(".")]
            
            # Ajustar comprimentos para comparação
            max_len = max(len(l_parts), len(c_parts))
            l_parts.extend([0] * (max_len - len(l_parts)))
            c_parts.extend([0] * (max_len - len(c_parts)))
            
            return l_parts > c_parts
        except Exception:
            return latest > current # Fallback para string
