import pytest
from pathlib import Path
from src.infrastructure.adapters.pymupdf_adapter import PyMuPDFAdapter
from src.domain.entities.pdf import PDFDocument

def test_pymupdf_adapter_merge(tmp_path):
    # Criar dois PDFs mínimos para teste
    import fitz
    pdf1_path = tmp_path / "test1.pdf"
    pdf2_path = tmp_path / "test2.pdf"
    output_path = tmp_path / "merged.pdf"
    
    doc1 = fitz.open()
    doc1.new_page()
    doc1.save(str(pdf1_path))
    doc1.close()
    
    doc2 = fitz.open()
    doc2.new_page()
    doc2.save(str(pdf2_path))
    doc2.close()
    
    adapter = PyMuPDFAdapter()
    docs = [
        PDFDocument(pdf1_path, "test1.pdf", 1),
        PDFDocument(pdf2_path, "test2.pdf", 1)
    ]
    
    result = adapter.merge(docs, output_path)
    
    assert result.exists()
    final_doc = fitz.open(str(result))
    assert final_doc.page_count == 2
    final_doc.close()

def test_pymupdf_adapter_split(tmp_path):
    import fitz
    input_path = tmp_path / "input.pdf"
    output_path = tmp_path / "split.pdf"
    
    doc = fitz.open()
    doc.new_page() # p1
    doc.new_page() # p2
    doc.new_page() # p3
    doc.save(str(input_path))
    doc.close()
    
    adapter = PyMuPDFAdapter()
    pdf = PDFDocument(input_path, "input.pdf", 3)
    
    # Extrair página 1 e 3 (0-based: 0 e 2)
    result = adapter.split(pdf, [0, 2], output_path)
    
    assert result.exists()
    final_doc = fitz.open(str(result))
    assert final_doc.page_count == 2
    final_doc.close()
