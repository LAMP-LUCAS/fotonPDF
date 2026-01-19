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
    assert output_path.name.startswith("sample_rotated")
    
    # Verify rotation in saved file
    new_doc = fitz.open(str(output_path))
    assert new_doc[0].rotation == 90
    new_doc.close()

def test_pymupdf_adapter_export_image(tmp_path):
    # Arrange
    pdf_path = tmp_path / "sample.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "Image Test")
    doc.save(str(pdf_path))
    doc.close()
    
    adapter = PyMuPDFAdapter()
    output_dir = tmp_path
    
    # Act - Export All (1 page)
    results = adapter.export_page_to_image(pdf_path, None, output_dir)
    
    # Assert
    assert len(results) == 1
    assert "PG" not in results[0].name # 1 página -> sem PG
    assert results[0].exists()

def test_pymupdf_adapter_export_image_multipage(tmp_path):
    pdf_path = tmp_path / "multi.pdf"
    doc = fitz.open()
    doc.new_page()
    doc.new_page()
    doc.save(str(pdf_path))
    doc.close()
    
    adapter = PyMuPDFAdapter()
    results = adapter.export_page_to_image(pdf_path, None, tmp_path)
    
    assert len(results) == 2
    assert "PG1" in results[0].name
    assert "PG2" in results[1].name

def test_pymupdf_adapter_export_svg_bulk(tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "SVG Test")
    doc.save(str(pdf_path))
    doc.close()
    
    adapter = PyMuPDFAdapter()
    output_dir = tmp_path
    
    results = adapter.export_page_to_svg(pdf_path, None, output_dir)
    
    assert len(results) == 1
    assert "PG" not in results[0].name # 1 página -> sem PG
    assert "<svg" in results[0].read_text(encoding="utf-8")

def test_pymupdf_adapter_export_markdown(tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "Markdown Test Content")
    doc.save(str(pdf_path))
    doc.close()
    
    adapter = PyMuPDFAdapter()
    dummy_out = tmp_path / "sample.md"
    
    result = adapter.export_to_markdown(pdf_path, dummy_out)
    
    assert result.exists()
    assert result.suffix == ".md"
    content = result.read_text(encoding="utf-8")
    assert "# Página 1" in content
    assert "Markdown Test Content" in content
