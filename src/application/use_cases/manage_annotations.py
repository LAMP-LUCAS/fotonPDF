
import datetime
import uuid
from src.infrastructure.repositories.annotation_repository import AnnotationRepository

class ManageAnnotationsUseCase:
    """
    Caso de Uso unificado para gerenciamento de anotações (CRUD).
    Encapusla a lógica de negócio e persiste via Repository.
    """

    def __init__(self, repository: AnnotationRepository):
        self._repo = repository

    def get_annotations(self, doc_path: str) -> list[dict]:
        """Recupera todas as anotações de um documento."""
        return self._repo.load(doc_path)

    def add_annotation(self, doc_path: str, page_index: int, text: str, author: str = "User") -> dict:
        """Cria e salva uma nova anotação."""
        annotations = self._repo.load(doc_path)
        
        new_ann = {
            "id": str(uuid.uuid4()),
            "page_index": page_index,
            "text": text,
            "author": author,
            "created_at": datetime.datetime.now().isoformat()
        }
        
        annotations.append(new_ann)
        self._repo.save(doc_path, annotations)
        return new_ann

    def remove_annotation(self, doc_path: str, annotation_id: str):
        """Remove uma anotação pelo ID."""
        annotations = self._repo.load(doc_path)
        
        # Filtra a lista removendo o item com o ID correspondente
        new_list = [a for a in annotations if a["id"] != annotation_id]
        
        if len(new_list) < len(annotations):
            self._repo.save(doc_path, new_list)
