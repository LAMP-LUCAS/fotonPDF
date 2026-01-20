import pytest
import fitz
from pathlib import Path
from src.infrastructure.adapters.pymupdf_adapter import PyMuPDFAdapter

def test_search_text_found(tmp_path):
    # Arrange
    pdf_path = tmp_path / "search_test.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "Hello fotonPDF world")
    doc.save(str(pdf_path))
    doc.close()
    
    adapter = PyMuPDFAdapter()
    
    # Act
    results = adapter.search_text(pdf_path, "fotonPDF")
    
    # Assert
    assert len(results) == 1
    assert results[0].page_index == 0
    assert "fotonPDF" in results[0].text_snippet
    assert len(results[0].highlights) > 0 # Rectangles found

def test_search_text_not_found(tmp_path):
    pdf_path = tmp_path / "search_test.pdf"
    doc = fitz.open()
    doc.new_page()
    doc.save(str(pdf_path))
    doc.close()
    
    adapter = PyMuPDFAdapter()
    results = adapter.search_text(pdf_path, "missing")
    
    assert len(results) == 0

def test_get_toc_success(tmp_path):
    # Arrange
    pdf_path = tmp_path / "toc_test.pdf"
    doc = fitz.open()
    doc.new_page() # Page 0
    doc.new_page() # Page 1
    
    # Bookmark for page 1
    doc.set_toc([
        [1, "Chapter 1", 2] # Level 1, Title, Page (1-based)
    ])
    
    doc.save(str(pdf_path))
    doc.close()
    
    adapter = PyMuPDFAdapter()
    
    # Act
    toc = adapter.get_toc(pdf_path)
    
    # Assert
    assert len(toc) == 1
    assert toc[0].title == "Chapter 1"
    assert toc[0].page_index == 1 # Converted to 0-based
    assert toc[0].level == 1
