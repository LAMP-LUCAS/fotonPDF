from typing import Optional, Any
from pydantic import BaseModel
from src.domain.services.ai_provider import LLMProvider, AIResponse
from src.infrastructure.services.logger import log_debug, log_error

class LiteLLMProvider(LLMProvider):
    """
    Implementação baseada em LiteLLM para suportar +100 provedores (OpenAI, Ollama, OpenRouter).
    Utiliza Instructor para garantir extração de dados estruturados (AEC Compliance).
    
    IMPORTANTE: Todas as importações de litellm/instructor são feitas de forma LAZY
    para evitar bloqueio da GUI durante a inicialização.
    """
    def __init__(self, model_name: str, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.model = model_name
        self.api_key = api_key
        self.base_url = base_url
        self._client = None  # Lazy initialized
        self._litellm = None  # Lazy imported

    def _ensure_loaded(self):
        """Carrega as bibliotecas de IA apenas quando necessário (Lazy Loading)."""
        if self._litellm is None:
            log_debug("LiteLLMProvider: Carregando bibliotecas de IA...")
            import litellm
            import instructor
            self._litellm = litellm
            self._client = instructor.from_litellm(litellm.completion)
            log_debug("LiteLLMProvider: Bibliotecas carregadas com sucesso.")

    def completion(self, prompt: str, system_prompt: Optional[str] = None, 
                   schema: Optional[type[BaseModel]] = None) -> AIResponse:
        """Executa uma chamada síncrona com suporte a schema estruturado."""
        self._ensure_loaded()
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            kwargs = {
                "model": self.model,
                "messages": messages,
                "api_key": self.api_key,
                "base_url": self.base_url
            }

            if schema:
                response = self._client(response_model=schema, **kwargs)
                return AIResponse(
                    text="Structured data extracted.",
                    structured_data=response.dict(),
                    provider=self.model.split("/")[0],
                    model=self.model
                )
            else:
                response = self._litellm.completion(**kwargs)
                content = response.choices[0].message.content
                return AIResponse(
                    text=content,
                    provider=response.get("provider", "unknown"),
                    model=self.model,
                    usage=response.get("usage", {})
                )

        except Exception as e:
            log_error(f"AI Provider Error ({self.model}): {str(e)}")
            raise

    def stream_completion(self, prompt: str, system_prompt: Optional[str] = None):
        """Implementação futura para streaming na interface."""
        pass
