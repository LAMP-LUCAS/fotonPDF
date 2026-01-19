from pathlib import Path
from datetime import datetime

class NamingService:
    """
    Centro de Verdade para nomenclatura de arquivos no fotonPDF.
    Garante coesão, coerência e segurança nos nomes de saída.
    """

    @staticmethod
    def get_timestamp() -> str:
        """Centraliza o formato de timestamp do sistema."""
        return datetime.now().strftime("%Y%m%d_%H%M%S_%f")

    @staticmethod
    def generate_output_path(
        base_path: Path, 
        output_dir: Path, 
        page_index: int | None = None, 
        total_pages: int = 1, 
        suffix: str = "",
        tag: str = ""
    ) -> Path:
        """
        Gera um caminho de saída seguindo as regras de negócio:
        - Se total_pages > 1 e page_index não é None: Nome_PGx_TimeStamp.ext
        - Caso contrário: Nome_TimeStamp.ext (ou Nome_tag_TimeStamp.ext se tag for provida)
        
        Args:
            base_path: Caminho do arquivo original.
            output_dir: Diretório ou arquivo de destino.
            page_index: Índice da página (0-based) ou None.
            total_pages: Total de páginas no documento original.
            suffix: Extensão do arquivo (ex: .png).
            tag: Tag opcional (ex: rotated, split).
        """
        timestamp = NamingService.get_timestamp()
        
        # Determinar base de nome
        stem = base_path.stem
        
        # Lógica de "PG" condicional
        pg_part = ""
        if total_pages > 1 and page_index is not None:
            pg_part = f"_PG{page_index + 1}"
            
        # Lógica de Tag
        tag_part = f"_{tag}" if tag else ""
        
        filename = f"{stem}{tag_part}{pg_part}_{timestamp}{suffix}"
        
        # Se output_dir for um diretório, anexamos o filename
        # Se for um arquivo (ex: passado via -o), respeitamos o diretório do arquivo 
        # mas injetamos nossa nomenclatura para garantir unicidade/timestamp conforme solicitado.
        if output_dir.is_dir():
            return output_dir / filename
        else:
            return output_dir.parent / filename
