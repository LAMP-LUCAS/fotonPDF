
import pytest
import os
from pathlib import Path
from src.interfaces.gui.main_window import MainWindow

@pytest.fixture
def stress_pdfs():
    """Retorna caminhos absolutos para os arquivos de teste gerados."""
    base_dir = Path("test_files")
    return {
        "large_a0": base_dir / "test_A0.pdf",
        "complex_vectors": base_dir / "test_complex_vectors.pdf",
        "multi_page_text": base_dir / "test_multi_page_text.pdf"
    }

@pytest.fixture
def main_window(qtbot, mocker):
    """Fixture da janela principal com mocks essenciais para evitar I/O e threads reais desnecessárias."""
    # Mock Services
    mocker.patch("src.infrastructure.services.resource_service.ResourceService.get_logo_ico")
    
    # Retorna uma instância limpa da janela
    window = MainWindow()
    qtbot.addWidget(window)
    return window
