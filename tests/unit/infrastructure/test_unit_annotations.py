
import pytest
from pathlib import Path
from src.infrastructure.repositories.annotation_repository import AnnotationRepository
from src.application.use_cases.manage_annotations import ManageAnnotationsUseCase

@pytest.fixture
def temp_repo(tmp_path):
    return AnnotationRepository(storage_dir=tmp_path)

@pytest.fixture
def use_case(temp_repo):
    return ManageAnnotationsUseCase(temp_repo)

def test_repo_save_and_load(temp_repo):
    doc_path = "C:/test/doc.pdf"
    annotations = [
        {"id": "1", "page_index": 0, "text": "Hello", "author": "User"}
    ]
    
    temp_repo.save(doc_path, annotations)
    loaded = temp_repo.load(doc_path)
    
    assert len(loaded) == 1
    assert loaded[0]["text"] == "Hello"

def test_use_case_add_annotation(use_case):
    doc_path = "C:/test/doc.pdf"
    ann = use_case.add_annotation(doc_path, 2, "Important Note")
    
    assert ann["text"] == "Important Note"
    assert ann["page_index"] == 2
    assert "id" in ann
    
    # Verify persistence
    loaded = use_case.get_annotations(doc_path)
    assert len(loaded) == 1
    assert loaded[0]["id"] == ann["id"]

def test_use_case_remove_annotation(use_case):
    doc_path = "C:/test/doc.pdf"
    ann = use_case.add_annotation(doc_path, 1, "To Delete")
    
    loaded_before = use_case.get_annotations(doc_path)
    assert len(loaded_before) == 1
    
    use_case.remove_annotation(doc_path, ann["id"])
    
    loaded_after = use_case.get_annotations(doc_path)
    assert len(loaded_after) == 0
