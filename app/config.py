"""
Centralized configuration. Loads values from .env using pydantic-settings.
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_name: str
    db_user: str
    db_password: str
    db_host: str = "localhost"
    db_port: str = "5432"

    # No longer required now that embeddings run locally, kept optional
    # in case you switch back to OpenAI/OpenRouter for chat later.
    openai_api_key: str = ""
    embedding_model: str = "all-MiniLM-L6-v2"
    embedding_dim: int = 384

    # OpenRouter — used for the RAG chat/answer step (free-tier model)
    openrouter_api_key: str = ""
    openrouter_model: str = "deepseek/deepseek-chat-v3:free"

    upload_dir: str = "uploaded_pdfs"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
