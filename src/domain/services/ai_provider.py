from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

class AIResponse(BaseModel):
    """Resposta padronizada da IA para garantir coesão no sistema."""
    text: str
    structured_data: Optional[Dict[str, Any]] = None
    provider: str
    model: str
    usage: Dict[str, int] = {}

class LLMProvider(ABC):
    """Interface abstrata para provedores de IA (Ollama, OpenAI, Gemini, etc)."""
    @abstractmethod
    def completion(self, prompt: str, system_prompt: Optional[str] = None, 
                   schema: Optional[type[BaseModel]] = None) -> AIResponse:
        pass

    @abstractmethod
    def stream_completion(self, prompt: str, system_prompt: Optional[str] = None):
        pass
