import pytest
from unittest.mock import MagicMock
from pathlib import Path
from src.application.use_cases.export_markdown import ExportMarkdownUseCase
from src.domain.ports.pdf_operations import PDFOperationsPort

def test_export_markdown_use_case(tmp_path):
    # Arrange
    mock_adapter = MagicMock(spec=PDFOperationsPort)
    use_case = ExportMarkdownUseCase(mock_adapter)
    
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_text("dummy content")
    
    output_path = tmp_path / "out.md"
    mock_adapter.export_to_markdown.return_value = output_path
    
    # Act
    result = use_case.execute(pdf_path, output_path)
    
    # Assert
    assert result == output_path
    mock_adapter.export_to_markdown.assert_called_once_with(pdf_path, output_path)
