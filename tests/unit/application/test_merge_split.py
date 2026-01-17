import pytest
from pathlib import Path
from unittest.mock import MagicMock, ANY
from src.application.use_cases.merge_pdf import MergePDFUseCase
from src.application.use_cases.split_pdf import SplitPDFUseCase
from src.domain.entities.pdf import PDFDocument
from src.domain.ports.pdf_operations import PDFOperationsPort

def test_merge_pdf_use_case():
    mock_ops = MagicMock(spec=PDFOperationsPort)
    use_case = MergePDFUseCase(mock_ops)
    
    input_paths = [Path("file1.pdf"), Path("file2.pdf")]
    output_path = Path("merged.pdf")
    
    # We need to monkeypatch Path.exists because it's a real class
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(Path, "exists", lambda x: True)
        mock_ops.get_info.side_effect = [
            PDFDocument(Path("file1.pdf"), "file1.pdf", 10),
            PDFDocument(Path("file2.pdf"), "file2.pdf", 5)
        ]
        mock_ops.merge.return_value = output_path
        
        result = use_case.execute(input_paths, output_path)
    
    assert result == output_path
    assert mock_ops.merge.called

def test_split_pdf_use_case():
    mock_ops = MagicMock(spec=PDFOperationsPort)
    use_case = SplitPDFUseCase(mock_ops)
    
    input_path = Path("input.pdf")
    pages = [1, 3, 5]
    output_path = Path("split.pdf")
    
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(Path, "exists", lambda x: True)
        mock_ops.get_info.return_value = PDFDocument(input_path, "input.pdf", 10)
        mock_ops.split.return_value = output_path
        
        result = use_case.execute(input_path, pages, output_path)
    
    assert result == output_path
    # Check if converted to 0-based
    mock_ops.split.assert_called_with(ANY, [0, 2, 4], output_path)
