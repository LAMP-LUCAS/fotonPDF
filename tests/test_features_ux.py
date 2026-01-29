
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from src.application.use_cases.add_annotation import AddAnnotationUseCase
from src.domain.ports.pdf_operations import PDFOperationsPort

def test_add_annotation_use_case_success():
    # Setup
    mock_port = MagicMock(spec=PDFOperationsPort)
    expected_path = Path("test_highlight.pdf")
    mock_port.add_annotation.return_value = expected_path
    
    uc = AddAnnotationUseCase(mock_port)
    src_file = Path("test.pdf")
    
    # Exec
    with patch("pathlib.Path.exists", return_value=True):
        result = uc.execute(src_file, 0, (10, 10, 100, 100), type="highlight", color=(1, 1, 0))
    
    # Assert
    assert result == expected_path
    mock_port.add_annotation.assert_called_once_with(
        src_file, 0, (10, 10, 100, 100), type="highlight", color=(1, 1, 0)
    )

def test_add_annotation_file_not_found():
    mock_port = MagicMock(spec=PDFOperationsPort)
    uc = AddAnnotationUseCase(mock_port)
    
    with pytest.raises(FileNotFoundError):
        # exists will return False by default on non-existent real files, 
        # but we can rely on real filesystem or patch it.
        # Here we rely on the fact that "non_existent.pdf" likely doesn't exist
        uc.execute(Path("non_existent_random_file.pdf"), 0, (0,0,0,0))
