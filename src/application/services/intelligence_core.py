from typing import Dict, Optional
from src.domain.services.ai_provider import LLMProvider
from src.infrastructure.services.settings_service import SettingsService
from src.infrastructure.services.logger import log_debug, log_error

class IntelligenceCore:
    """
    Orquestrador Central de Inteligência.
    Gerencia a troca dinâmica de modelos e a resiliência entre local (Ollama) e nuvem.
    
    IMPORTANTE: A criação do provider é LAZY para não bloquear a GUI.
    """
    def __init__(self):
        self._providers: Dict[str, LLMProvider] = {}
        self._active_provider_name: str = "default"
        self._settings = SettingsService.instance()
        self._initialized = False

    def _ensure_initialized(self):
        """Inicializa o provider padrão apenas quando necessário (Lazy Loading)."""
        if self._initialized:
            return
        
        log_debug("IntelligenceCore: Inicializando provider de IA...")
        try:
            from src.infrastructure.services.ai_litellm_provider import LiteLLMProvider
            
            provider_name = self._settings.get("ai_provider", "ollama")
            model = self._settings.get("ai_model", "llama3")
            api_key = self._settings.get("ai_api_key", None)
            base_url = self._settings.get("ai_base_url", "http://localhost:11434")

            model_string = f"{provider_name}/{model}" if provider_name != "ollama" else f"ollama/{model}"
            
            self._providers["default"] = LiteLLMProvider(
                model_name=model_string,
                api_key=api_key,
                base_url=base_url
            )
            self._initialized = True
            log_debug("IntelligenceCore: Provider inicializado com sucesso.")
        except Exception as e:
            log_error(f"IntelligenceCore: Falha ao inicializar provider: {e}")
            self._initialized = True  # Marca como inicializado para não tentar novamente

    def get_provider(self) -> Optional[LLMProvider]:
        """Retorna o provider ativo, inicializando-o se necessário."""
        self._ensure_initialized()
        return self._providers.get("default")

    def switch_model(self, provider_name: str, model: str, api_key: Optional[str] = None):
        """Troca o modelo ativo em tempo de execução (Modularidade)."""
        from src.infrastructure.services.ai_litellm_provider import LiteLLMProvider
        new_provider = LiteLLMProvider(f"{provider_name}/{model}", api_key=api_key)
        self._providers["default"] = new_provider
        self._settings.set("ai_provider", provider_name)
        self._settings.set("ai_model", model)
        if api_key:
            self._settings.set("ai_api_key", api_key)
