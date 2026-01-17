from pathlib import Path
from typing import List
from src.domain.entities.pdf import PDFDocument
from src.domain.ports.pdf_operations import PDFOperationsPort

class MergePDFUseCase:
    """Caso de uso para unir múltiplos documentos PDF em um único arquivo."""

    def __init__(self, pdf_ops: PDFOperationsPort):
        self._pdf_ops = pdf_ops

    def execute(self, input_paths: List[Path], output_path: Path) -> Path:
        """
        Une os arquivos informados na ordem da lista.
        
        Args:
            input_paths: Lista de caminhos para os PDFs originais.
            output_path: Caminho de destino para o arquivo unido.
            
        Returns:
            Path: Caminho do arquivo final.
        """
        if not input_paths:
            raise ValueError("A lista de arquivos para união não pode estar vazia.")

        documents = []
        for path in input_paths:
            if not path.exists():
                raise FileNotFoundError(f"Arquivo não encontrado: {path}")
            documents.append(self._pdf_ops.get_info(path))

        return self._pdf_ops.merge(documents, output_path)
