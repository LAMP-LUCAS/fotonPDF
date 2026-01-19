import pytest
from unittest.mock import MagicMock
from pathlib import Path
from src.application.use_cases.export_svg import ExportSVGUseCase
from src.domain.ports.pdf_operations import PDFOperationsPort

def test_export_svg_use_case(tmp_path):
    # Arrange
    mock_adapter = MagicMock(spec=PDFOperationsPort)
    use_case = ExportSVGUseCase(mock_adapter)
    
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_text("dummy content")
    
    output_dir = tmp_path
    mock_adapter.export_page_to_svg.return_value = [output_dir / "test_PG1_123.svg"]
    
    # Act
    result = use_case.execute(pdf_path, 0, output_dir)
    
    # Assert
    assert isinstance(result, list)
    assert result[0].name.startswith("test_PG1")
    mock_adapter.export_page_to_svg.assert_called_once_with(pdf_path, 0, output_dir)
