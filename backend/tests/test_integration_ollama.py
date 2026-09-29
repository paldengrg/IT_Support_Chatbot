"""Runs against the real local Ollama; skipped automatically when it is not running."""

import asyncio

import httpx
import pytest
from fastapi.testclient import TestClient

from app.api.chat import SOURCES_MARKER
from app.core.config import get_settings
from app.services.ollama import OllamaClient

SETTINGS = get_settings()


def _ollama_up() -> bool:
    try:
        return httpx.get(f"{SETTINGS.ollama_url}/api/tags", timeout=2).status_code == 200
    except httpx.HTTPError:
        return False


pytestmark = pytest.mark.skipif(not _ollama_up(), reason="Ollama is not running")


def test_real_embed_and_chat():
    async def run():
        client = OllamaClient(SETTINGS.ollama_url, SETTINGS.chat_model, SETTINGS.embed_model)
        try:
            vectors = await client.embed(["search_document: hello"])
            tokens = [t async for t in client.chat_stream([{"role": "user", "content": "Reply with the word OK."}])]
        finally:
            await client.aclose()
        return vectors, tokens

    vectors, tokens = asyncio.run(run())
    assert len(vectors[0]) == 768
    assert "".join(tokens).strip()


def test_end_to_end_chat_request():
    from app.main import app

    with TestClient(app) as client:
        resp = client.post("/api/chat", json={"message": "My Wi-Fi keeps disconnecting on Windows 11"})
    assert resp.status_code == 200
    assert SOURCES_MARKER in resp.text
