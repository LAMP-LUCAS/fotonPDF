from pathlib import Path
from src.domain.entities.pdf import PDFDocument
from src.domain.ports.pdf_operations import PDFOperationsPort

class RotatePDFUseCase:
    """Caso de uso para rotacionar um documento PDF."""

    def __init__(self, pdf_ops: PDFOperationsPort):
        self._pdf_ops = pdf_ops

    def execute(self, input_path: Path, degrees: int) -> Path:
        """
        Executa a rotação e retorna o caminho do novo arquivo.
        
        Args:
            input_path: Caminho do PDF original.
            degrees: Graus (90, 180, 270).
            
        Returns:
            Path: Caminho do arquivo rotacionado.
        """
        if not input_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {input_path}")
            
        if degrees not in [90, 180, 270]:
            raise ValueError("Graus de rotação devem ser 90, 180 ou 270.")

        pdf = self._pdf_ops.get_info(input_path)
        return self._pdf_ops.rotate(pdf, degrees)
