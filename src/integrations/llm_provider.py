from abc import ABC, abstractmethod
from tenacity import retry, stop_after_attempt, wait_exponential
from langchain_openai import ChatOpenAI
from src.core.config import get_settings


class LLMProvider(ABC):
    @abstractmethod
    def get_llm(self): ...

    @abstractmethod
    def get_name(self) -> str: ...


class OpenAIProvider(LLMProvider):
    def __init__(self, model: str = None, temperature: float = 0.7):
        settings = get_settings()
        self.model = model or settings.primary_llm
        self.temperature = temperature

    def get_llm(self) -> ChatOpenAI:
        settings = get_settings()
        return ChatOpenAI(
            model=self.model,
            temperature=self.temperature,
            api_key=settings.openai_api_key,
        )

    def get_name(self) -> str:
        return f"openai/{self.model}"


class OpenAIFallbackProvider(OpenAIProvider):
    """Cheaper fallback for simple tasks."""
    def __init__(self, temperature: float = 0.3):
        settings = get_settings()
        super().__init__(model=settings.fallback_llm, temperature=temperature)

    def get_name(self) -> str:
        return f"openai-fallback/{self.model}"


def get_primary_llm(temperature: float = 0.7) -> ChatOpenAI:
    return OpenAIProvider(temperature=temperature).get_llm()


def get_fallback_llm(temperature: float = 0.3) -> ChatOpenAI:
    return OpenAIFallbackProvider(temperature=temperature).get_llm()


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def invoke_with_retry(llm, messages: list) -> str:
    """Invoke an LLM with automatic exponential backoff on failure."""
    response = llm.invoke(messages)
    return response.content
