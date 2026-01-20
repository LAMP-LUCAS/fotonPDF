import pytest
import fitz
from pathlib import Path
from src.infrastructure.adapters.pymupdf_adapter import PyMuPDFAdapter

def test_has_text_layer_true(tmp_path):
    pdf_path = tmp_path / "text.pdf"
    doc = fitz.open()
    page = doc.new_page()
    # Inserir texto suficiente para ser considerado pesquisável (> 50 caracteres)
    page.insert_text((50, 50), "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.")
    doc.save(str(pdf_path))
    doc.close()
    
    adapter = PyMuPDFAdapter()
    assert adapter.has_text_layer(pdf_path) is True

def test_has_text_layer_false(tmp_path):
    pdf_path = tmp_path / "image.pdf"
    doc = fitz.open()
    page = doc.new_page()
    # Página sem texto (apenas imagem ou pouquíssimo texto)
    page.insert_text((50, 50), "Scan")
    doc.save(str(pdf_path))
    doc.close()
    
    adapter = PyMuPDFAdapter()
    assert adapter.has_text_layer(pdf_path) is False

def test_ocr_engine_available():
    adapter = PyMuPDFAdapter()
    # Este teste depende do ambiente, mas verifica se a lógica de detecção não explode
    result = adapter.is_engine_available()
    assert isinstance(result, bool)
