from pathlib import Path

from app.core.config import BACKEND_DIR, Settings


def test_backend_dir_points_at_backend_folder():
    assert (BACKEND_DIR / "app" / "core" / "config.py").is_file()


def test_resolve_relative_path_is_anchored_to_backend_dir():
    settings = Settings()
    assert settings.resolve("./chroma_db") == (BACKEND_DIR / "chroma_db").resolve()


def test_resolve_keeps_absolute_path(tmp_path):
    settings = Settings()
    assert settings.resolve(str(tmp_path)) == Path(tmp_path)


def test_defaults():
    settings = Settings(_env_file=None)
    assert settings.chat_model == "gemma2:2b"
    assert settings.embed_model == "nomic-embed-text"
    assert settings.rag_top_k == 4
    assert settings.rag_max_distance == 0.5
