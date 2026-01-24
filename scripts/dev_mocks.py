import json
from pathlib import Path
from typing import List, Dict

class FakeDataGenerator:
    """
    Gera dados fakes para popular o mockup da interface do fotonPDF.
    Centraliza a 'verdade' dos mocks para garantir DRY entre Qt e Web Concept.
    """
    
    @staticmethod
    def get_all_data() -> Dict:
        """Retorna todos os mocks em um único dicionário para fácil exportação."""
        return {
            "documents": FakeDataGenerator.get_fake_documents(),
            "toc": FakeDataGenerator.get_fake_toc(),
            "search": FakeDataGenerator.get_fake_search_results(),
            "annotations": FakeDataGenerator.get_fake_annotations(),
            "system_status": {
                "engine": "PyMuPDF 1.23.0",
                "aec_mode": "Focused",
                "memory": "156MB"
            }
        }

    @staticmethod
    def export_to_json(output_path: str):
        """Exporta os dados mockados para um arquivo JSON consumível por web prototypes."""
        data = FakeDataGenerator.get_all_data()
        # Converte Path para string para ser serializável
        for doc in data["documents"]:
            if isinstance(doc["path"], Path):
                doc["path"] = str(doc["path"])
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    @staticmethod
    def get_fake_documents() -> List[Dict]:
        return [
            {"path": "C:/AEC/Projetos/Planta_Baixa_A0.pdf", "name": "Planta_Baixa_A0.pdf", "pages": 1, "type": "drawing"},
            {"path": "C:/AEC/Projetos/Memorial_Descritivo.pdf", "name": "Memorial_Descritivo.pdf", "pages": 45, "type": "text"},
            {"path": "C:/AEC/Projetos/Corte_Arquitetonico.pdf", "name": "Corte_Arquitetonico.pdf", "pages": 3, "type": "drawing"},
            {"path": "C:/AEC/Contratos/Acordo_Nivel_Servico.pdf", "name": "Acordo_Nivel_Servico.pdf", "pages": 12, "type": "text"},
        ]

    @staticmethod
    def get_fake_toc() -> List[Dict]:
        return [
            {"title": "1. Introdução", "page": 1, "level": 0},
            {"title": "2. Especificações Técnicas", "page": 5, "level": 0},
            {"title": "2.1 Elétrica", "page": 10, "level": 1},
            {"title": "2.2 Hidráulica", "page": 15, "level": 1},
            {"title": "3. Cronograma", "page": 40, "level": 0},
        ]

    @staticmethod
    def get_fake_search_results() -> List[Dict]:
        return [
            {"text": "...conforme a planta de **fundação** na página 4...", "page": 4},
            {"text": "...o reforço na **fundação** deve seguir a norma...", "page": 10},
            {"text": "...verificar profundidade da **fundação**...", "page": 42},
        ]

    @staticmethod
    def get_fake_annotations() -> List[Dict]:
        return [
            {"type": "highlight", "page": 2, "text": "Revisar este cálculo", "color": "#FFFF00"},
            {"type": "text", "page": 5, "text": "Confirmar com o engenheiro", "color": "#FFC0CB"},
        ]
