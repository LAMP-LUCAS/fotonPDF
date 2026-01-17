import pytest
from unittest.mock import MagicMock
from pathlib import Path
from src.application.use_cases.rotate_pdf import RotatePDFUseCase
from src.domain.ports.pdf_operations import PDFOperationsPort
from src.domain.entities.pdf import PDFDocument

def test_rotate_pdf_use_case():
    # Arrange
    mock_adapter = MagicMock(spec=PDFOperationsPort)
    use_case = RotatePDFUseCase(mock_adapter)
    
    input_path = Path("test.pdf")
    # Simular que arquivo existe para o teste de lógica
    with open(input_path, "w") as f: f.write("") 
    
    mock_adapter.get_info.return_value = PDFDocument(input_path, "test.pdf", 1)
    mock_adapter.rotate.return_value = Path("test_rotated.pdf")
    
    # Act
    result = use_case.execute(input_path, 90)
    
    # Assert
    assert result == Path("test_rotated.pdf")
    mock_adapter.get_info.assert_called_once_with(input_path)
    mock_adapter.rotate.assert_called_once()
    
    # Cleanup
    input_path.unlink()

def test_rotate_pdf_invalid_degrees(tmp_path):
    mock_adapter = MagicMock(spec=PDFOperationsPort)
    use_case = RotatePDFUseCase(mock_adapter)
    
    input_path = tmp_path / "dummy.pdf"
    input_path.write_text("content")
    
    with pytest.raises(ValueError, match="Graus de rotação devem ser 90, 180 ou 270."):
        use_case.execute(input_path, 45)

