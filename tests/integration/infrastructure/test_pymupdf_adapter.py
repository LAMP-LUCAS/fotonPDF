import pytest
import fitz
from pathlib import Path
from src.infrastructure.adapters.pymupdf_adapter import PyMuPDFAdapter

def test_pymupdf_adapter_rotation(tmp_path):
    # Arrange
    pdf_path = tmp_path / "sample.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "fotonPDF Test")
    doc.save(str(pdf_path))
    doc.close()
    
    adapter = PyMuPDFAdapter()
    pdf_info = adapter.get_info(pdf_path)
    
    # Act
    output_path = adapter.rotate(pdf_info, 90)
    
    # Assert
    assert output_path.exists()
    assert output_path.name == "sample_rotated.pdf"
    
    # Verify rotation in saved file
    new_doc = fitz.open(str(output_path))
    assert new_doc[0].rotation == 90
    new_doc.close()
