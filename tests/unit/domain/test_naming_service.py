import pytest
from pathlib import Path
from src.domain.services.naming_service import NamingService

from unittest.mock import patch

def test_naming_service_single_page(tmp_path):
    base = Path("doc.pdf")
    out = tmp_path / "outdir"
    out.mkdir()
    
    # 1 página, exportando a única página
    res = NamingService.generate_output_path(base, out, page_index=0, total_pages=1, suffix=".png")
    
    assert "PG" not in res.name
    assert "202" in res.name
    assert res.suffix == ".png"

def test_naming_service_multi_page(tmp_path):
    base = Path("doc.pdf")
    out = tmp_path / "outdir"
    out.mkdir()
    
    # 5 páginas, exportando a página 2
    res = NamingService.generate_output_path(base, out, page_index=1, total_pages=5, suffix=".png")
    
    assert "_PG2_" in res.name

def test_naming_service_with_tag(tmp_path):
    base = Path("doc.pdf")
    out = tmp_path / "outdir"
    out.mkdir()
    
    res = NamingService.generate_output_path(base, out, tag="rotated", suffix=".pdf")
    
    assert "_rotated_" in res.name
    assert "PG" not in res.name

def test_naming_service_output_file_provided(tmp_path):
    base = Path("doc.pdf")
    # Usuário passou um caminho de arquivo específico (que não existe como diretório)
    out = tmp_path / "dest" / "custom.pdf"
    out.parent.mkdir()
    
    res = NamingService.generate_output_path(base, out, suffix=".pdf")
    
    assert res.parent == out.parent
    assert res.name.startswith("doc")
