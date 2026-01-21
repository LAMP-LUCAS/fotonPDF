import pytest
from pathlib import Path
from src.infrastructure.adapters.pymupdf_adapter import PyMuPDFAdapter
from src.domain.entities.pdf import PDFDocument

def test_add_highlight_annotation(tmp_path):
    # Setup: Criar um PDF mínimo para teste
    import fitz
    test_pdf = tmp_path / "test.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "Texto para realçar")
    doc.save(str(test_pdf))
    doc.close()
    
    adapter = PyMuPDFAdapter()
    rect = (45, 45, 150, 60) # Área aproximada do texto
    
    # Execute
    output_path = adapter.add_annotation(
        test_pdf, 
        page_index=0, 
        rect=rect, 
        type="highlight"
    )
    
    # Verify
    assert output_path.exists()
    assert "_highlight.pdf" in output_path.name
    
    # Verificar se a anotação existe no novo arquivo
    with fitz.open(str(output_path)) as final_doc:
        final_page = final_doc[0]
        annots = list(final_page.annots())
        assert len(annots) >= 1
        assert annots[0].type[0] == 8 # 8 é Highlight em PDF
