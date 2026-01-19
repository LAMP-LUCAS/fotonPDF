import pytest
from unittest.mock import MagicMock
from pathlib import Path
from src.application.use_cases.export_image import ExportImageUseCase
from src.domain.ports.pdf_operations import PDFOperationsPort

def test_export_image_use_case(tmp_path):
    # Arrange
    mock_adapter = MagicMock(spec=PDFOperationsPort)
    use_case = ExportImageUseCase(mock_adapter)
    
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_text("dummy content")
    
    output_dir = tmp_path
    mock_adapter.export_page_to_image.return_value = [output_dir / "test_PG1_123.png"]
    
    # Act
    result = use_case.execute(pdf_path, 0, output_dir, fmt="png", dpi=300)
    
    # Assert
    assert isinstance(result, list)
    assert result[0].name.startswith("test_PG1")
    mock_adapter.export_page_to_image.assert_called_once_with(pdf_path, 0, output_dir, "png", 300)

def test_export_image_file_not_found():
    mock_adapter = MagicMock(spec=PDFOperationsPort)
    use_case = ExportImageUseCase(mock_adapter)
    
    with pytest.raises(FileNotFoundError):
        use_case.execute(Path("non_existent.pdf"), 0, Path("out.png"))
