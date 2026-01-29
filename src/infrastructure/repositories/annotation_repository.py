
import json
from pathlib import Path
from src.infrastructure.services.logger import log_debug, log_exception

class AnnotationRepository:
    """
    Repositório responsável pela persistência de anotações do usuário.
    Implementação atual baseada em arquivos JSON (sidecar ou central).
    """

    def __init__(self, storage_dir: Path = None):
        if storage_dir:
            self.storage_dir = storage_dir
        else:
            # Default: salva na pasta .fotonPDF do usuário
            self.storage_dir = Path.home() / ".fotonPDF" / "annotations"
        
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _get_storage_path(self, doc_path: str) -> Path:
        """Gera um caminho único para o arquivo de anotações baseado no hash ou nome do arquivo."""
        # Simplificação: Usar nome do arquivo + hash simples do caminho
        import hashlib
        path_hash = hashlib.md5(str(doc_path).encode()).hexdigest()
        filename = f"{Path(doc_path).stem}_{path_hash[:8]}.json"
        return self.storage_dir / filename

    def load(self, doc_path: str) -> list[dict]:
        """Carrega e retorna a lista de anotações para um documento."""
        try:
            path = self._get_storage_path(doc_path)
            if not path.exists():
                return []
            
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("annotations", [])
        except Exception as e:
            log_exception(f"AnnotationRepository: Erro ao carregar notas de {doc_path}: {e}")
            return []

    def save(self, doc_path: str, annotations: list[dict]):
        """Salva a lista completa de anotações."""
        try:
            path = self._get_storage_path(doc_path)
            data = {
                "source_file": str(doc_path),
                "updated_at": "TODO_TIMESTAMP",
                "annotations": annotations
            }
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            log_debug(f"AnnotationRepository: {len(annotations)} notas salvas em {path}")
        except Exception as e:
            log_exception(f"AnnotationRepository: Erro ao salvar notas: {e}")
