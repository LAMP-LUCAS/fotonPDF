from typing import Dict, Optional
from src.domain.services.ai_provider import LLMProvider
from src.infrastructure.services.ai_litellm_provider import LiteLLMProvider
from src.infrastructure.services.settings_service import SettingsService

class IntelligenceCore:
    """
    Orquestrador Central de Inteligência.
    Gerencia a troca dinâmica de modelos e a resiliência entre local (Ollama) e nuvem.
    """
    def __init__(self):
        self._providers: Dict[str, LLMProvider] = {}
        self._active_provider_name: str = "default"
        self._settings = SettingsService.instance()
        self._initialize_from_settings()

    def _initialize_from_settings(self):
        """Configura os provedores baseados nas preferências do usuário."""
        # Exemplo de carregamento:
        # provider_type: 'ollama', 'openai', 'openrouter'
        # model: 'llama3', 'gpt-4o', etc.
        
        provider_name = self._settings.get("ai_provider", "ollama")
        model = self._settings.get("ai_model", "llama3")
        api_key = self._settings.get("ai_api_key", None)
        base_url = self._settings.get("ai_base_url", "http://localhost:11434")

        # Mapeamento para formato LiteLLM
        model_string = f"{provider_name}/{model}" if provider_name != "ollama" else f"ollama/{model}"
        
        self._providers["default"] = LiteLLMProvider(
            model_name=model_string,
            api_key=api_key,
            base_url=base_url
        )

    def get_provider(self) -> LLMProvider:
        return self._providers.get("default")

    def switch_model(self, provider_name: str, model: str, api_key: Optional[str] = None):
        """Troca o modelo ativo em tempo de execução (Moduralidade)."""
        new_provider = LiteLLMProvider(f"{provider_name}/{model}", api_key=api_key)
        self._providers["default"] = new_provider
        # Salvar nas configurações
        self._settings.set("ai_provider", provider_name)
        self._settings.set("ai_model", model)
        if api_key: self._settings.set("ai_api_key", api_key)
