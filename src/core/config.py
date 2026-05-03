from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # LLM
    openai_api_key: str
    anthropic_api_key: str = ""
    google_api_key: str = ""
    primary_llm: str = "gpt-4o"
    fallback_llm: str = "gpt-4o-mini"

    # Research
    serp_api_key: str
    max_search_results: int = 10
    research_cache_ttl: int = 1800  # seconds

    # Image
    image_model: str = "dall-e-3"
    image_fallback_model: str = "dall-e-2"

    # LangSmith
    langchain_tracing_v2: bool = False
    langchain_api_key: str = ""
    langchain_project: str = "contentalchemy"

    # Streamlit
    streamlit_server_port: int = 8501


@lru_cache
def get_settings() -> Settings:
    return Settings()
