"""Provider factory — returns the configured LLM provider instance."""
from app.ai.providers.base import LLMProvider, LLMProviderError


def get_provider() -> LLMProvider:
    """
    Instantiate and return the LLM provider configured in settings.

    The provider is determined by ``ENVFORGE_LLM_PROVIDER`` env var:
        - ``mock``       → deterministic responses for testing
        - ``openrouter`` → routes to 100+ models via OpenRouter API
        - ``openai``     → direct OpenAI API
        - ``ollama``     → local inference (not yet implemented)

    Returns:
        An instance of a class implementing :class:`LLMProvider`.

    Raises:
        LLMProviderError: If the configured provider is unknown or misconfigured.
    """
    from app.config import get_settings
    settings = get_settings()

    provider_name = settings.envforge_llm_provider.lower()

    if provider_name == "mock":
        from app.ai.providers.mock import MockProvider
        return MockProvider()

    if provider_name == "openrouter":
        from app.ai.providers.openrouter import OpenRouterProvider
        return OpenRouterProvider(
            api_key=settings.openrouter_api_key,
            model=settings.openrouter_model,
            max_tokens=settings.ai_max_tokens,
            temperature=settings.ai_temperature,
        )

    if provider_name == "openai":
        from app.ai.providers.openai import OpenAIProvider
        # Safely extract dynamic configuration values from environment context settings
        api_key = getattr(settings, "openai_api_key", None)
        base_url = getattr(settings, "openai_base_url", "https://api.openai.com/v1")

        return OpenAIProvider(
            api_key=api_key,
            base_url=base_url
        )

    if provider_name == "ollama":
        raise LLMProviderError(
            "ollama",
            "Ollama local provider is not yet implemented. "
            "Use 'openrouter' or 'mock' for now.",
        )

    raise LLMProviderError(
        provider_name,
        f"Unknown LLM provider: '{provider_name}'. "
        f"Valid options: mock, openrouter, openai, ollama.",
    )
