import os
import fitz
from pathlib import Path
from src.infrastructure.services.logger import log_debug

class DocumentAnalyzer:
    """
    Analisador Inteligente de Documentos.
    Classifica PDFs com base na complexidade visual e técnica para adaptar a estratégia de renderização.
    """
    
    @staticmethod
    def analyze(pdf_path: Path) -> dict:
        """
        Analisa o PDF e retorna um dicionário de 'hints' de performance.
        Classificações: LIGHT, STANDARD, HEAVY.
        """
        log_debug(f"Analyzer: Iniciando análise de {pdf_path.name}...")
        try:
            stats = {
                "complexity": "STANDARD",
                "is_vector_heavy": False,
                "is_large_dimensions": False,
                "estimated_load": "medium"
            }
            
            file_size = os.path.getsize(pdf_path)
            # Acima de 50MB é tendencialmente pesado
            if file_size > 50 * 1024 * 1024:
                stats["complexity"] = "HEAVY"
                stats["estimated_load"] = "high"

            doc = fitz.open(str(pdf_path))
            page_count = doc.page_count
            
            # Analisar uma amostra significativa (primeira página)
            page = doc[0]
            
            # Verificar dimensões (Arquitetura costuma usar A0, A1, etc)
            if page.rect.width > 2000 or page.rect.height > 2000:
                stats["is_large_dimensions"] = True
                stats["complexity"] = "HEAVY"

            # HEURÍSTICA DE SEGURANÇA: Se o arquivo for grande, get_drawings() 
            # pode travar o GIL. Vamos ser conservadores.
            if stats["complexity"] == "HEAVY" or file_size > 10 * 1024 * 1024:
                stats["is_vector_heavy"] = True # Assumimos peso para segurança
                log_debug(f"Analyzer: Arquivo grande ({file_size/1024/1024:.1f}MB). Pulando scan de vetores por performance.")
            else:
                paths = page.get_drawings()
                if len(paths) > 1000:
                    stats["is_vector_heavy"] = True
                    stats["complexity"] = "HEAVY"

            doc.close()
            log_debug(f"Analyzer: Concluído para {pdf_path.name} -> Mode: {stats['complexity']}")
            return stats
            
        except Exception as e:
            log_debug(f"Analyzer Error: {e}")
            return {"complexity": "STANDARD", "is_vector_heavy": False, "is_large_dimensions": False}
