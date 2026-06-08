from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Paper RAG Assistant"
    database_url: str = "sqlite:///./storage/app.db"
    storage_dir: Path = Path("storage")
    max_upload_bytes: int = 50 * 1024 * 1024
    embedding_dim: int = 64
    default_top_k: int = 8
    llm_provider: str = "fake"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="PAPER_RAG_")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.storage_dir.mkdir(parents=True, exist_ok=True)
    (settings.storage_dir / "papers").mkdir(parents=True, exist_ok=True)
    return settings
