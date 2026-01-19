from pathlib import Path
from src.domain.ports.pdf_operations import PDFOperationsPort

class ExportMarkdownUseCase:
    """Caso de uso para exportar o conteúdo do PDF como Markdown."""

    def __init__(self, pdf_ops: PDFOperationsPort):
        self._pdf_ops = pdf_ops

    def execute(self, pdf_path: Path, output_path: Path) -> Path:
        """
        Executa a exportação do texto do PDF para Markdown.
        
        Args:
            pdf_path: Caminho do PDF original.
            output_path: Caminho onde o arquivo .md será salvo.
            
        Returns:
            Path: Caminho do arquivo Markdown gerado.
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {pdf_path}")
            
        return self._pdf_ops.export_to_markdown(pdf_path, output_path)
