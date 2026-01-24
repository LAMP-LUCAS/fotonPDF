from typing import Optional, List, Dict, Any
from pathlib import Path
from src.domain.ports.pdf_operations import PDFOperationsPort
from src.application.use_cases.search_text import SearchTextUseCase
from src.application.use_cases.rotate_pdf import RotatePDFUseCase
from src.domain.entities.pdf import PDFDocument
from src.infrastructure.services.logger import log_debug, log_error

class CommandOrchestrator:
    """
    Orquestrador de comandos unificado para a Barra de Busca Superior.
    Distingue entre buscas de texto e execução de ações do sistema.
    
    IMPORTANTE: A inicialização da IA é LAZY para não bloquear a GUI.
    """
    
    def __init__(self, pdf_port: PDFOperationsPort):
        self.pdf_port = pdf_port
        self._ai = None  # Lazy initialized

    @property
    def ai(self):
        """Acesso lazy ao IntelligenceCore."""
        if self._ai is None:
            try:
                from src.application.services.intelligence_core import IntelligenceCore
                self._ai = IntelligenceCore()
                log_debug("CommandOrchestrator: IntelligenceCore carregado.")
            except Exception as e:
                log_error(f"CommandOrchestrator: Erro ao carregar IA: {e}")
        return self._ai

    def execute(self, query: str, active_pdf_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Interpreta a string e decide a ação.
        Suporta comandos diretos (ex: > girar) e tradução via IA (ex: > manda esse pdf pro lado).
        """
        query = query.strip()
        
        # Modo de Comando
        if query.startswith(">"):
            cmd_text = query[1:].strip()
            # 1. Tenta comando literal rápido (eficiência/economia)
            literal_res = self._handle_literal_command(cmd_text, active_pdf_path)
            if literal_res["type"] != "error":
                return literal_res
            
            # 2. Se falhar, usa IA para tradução semântica (se disponível)
            return self._handle_ai_translation(cmd_text, active_pdf_path)
        
        # Modo de Busca (Padrão)
        if active_pdf_path:
            use_case = SearchTextUseCase(self.pdf_port)
            results = use_case.execute(active_pdf_path, query)
            return {"type": "search", "query": query, "results": results}
        
        return {"type": "error", "message": "Nenhum documento ativo para busca."}

    def _handle_literal_command(self, cmd_text: str, pdf_path: Optional[Path]) -> Dict[str, Any]:
        """Processa comandos específicos rápidos."""
        cmd_text = cmd_text.lower()
        if cmd_text.startswith("girar") or cmd_text.startswith("rotate"):
            if not pdf_path:
                return {"type": "error", "message": "Carregue um PDF para girar."}
            degrees = 90
            if "180" in cmd_text:
                degrees = 180
            if "270" in cmd_text:
                degrees = 270
            use_case = RotatePDFUseCase(self.pdf_port)
            new_path = use_case.execute(pdf_path, degrees)
            return {"type": "command", "action": "rotate", "message": f"Documento rotacionado em {degrees}°", "path": str(new_path)}
        return {"type": "error", "message": "Comando literal não encontrado."}

    def _handle_ai_translation(self, cmd_text: str, pdf_path: Optional[Path]) -> Dict[str, Any]:
        """Usa a IA para traduzir linguagem natural em comandos do sistema."""
        if self.ai is None:
            return {"type": "error", "message": "Serviço de IA não disponível."}
        
        from src.application.services.ai_command_schema import CommandSchema
        try:
            provider = self.ai.get_provider()
            if provider is None:
                return {"type": "error", "message": "Provider de IA não inicializado."}
                
            prompt = f"O usuário deseja executar: '{cmd_text}'. "
            prompt += "Traduza isso para um comando do sistema fotonPDF."
            
            ai_res = provider.completion(
                prompt=prompt,
                system_prompt="Você é o orquestrador do fotonPDF. Traduza a intenção do usuário em comandos estruturados.",
                schema=CommandSchema
            )
            
            if ai_res.structured_data:
                data = ai_res.structured_data
                action = data.get("action")
                param = data.get("parameter")
                
                if action == "rotate":
                    return self._handle_literal_command(f"rotate {param if param else ''}", pdf_path)
                
                return {
                    "type": "command",
                    "explanation": data.get("explanation"),
                    "message": f"IA entendeu: {data.get('explanation')}"
                }
            
        except Exception as e:
            return {"type": "error", "message": f"Erro na tradução AI: {str(e)}"}
        
        return {"type": "error", "message": "Não consegui entender a intenção semântica."}
