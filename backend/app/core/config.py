from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BACKEND_DIR / ".env", extra="ignore")

    ollama_url: str = "http://localhost:11434"
    chat_model: str = "gemma2:2b"
    embed_model: str = "nomic-embed-text"
    chroma_path: str = "./chroma_db"
    rag_top_k: int = 4
    rag_max_distance: float = 0.5
    frontend_origin: str = "http://localhost:3000"
    licenses_path: str = "./data/licenses.json"
    knowledge_path: str = "./knowledge"

    def resolve(self, p: str) -> Path:
        """Resolve a configured path; relative paths are anchored to the backend folder."""
        path = Path(p)
        return path if path.is_absolute() else (BACKEND_DIR / path).resolve()


@lru_cache
def get_settings() -> Settings:
    return Settings()
