import asyncio
import json

import httpx
import pytest

from app.services.ollama import OllamaClient, OllamaError


def make_client(handler):
    return OllamaClient(
        "http://ollama.test",
        "gemma2:2b",
        "nomic-embed-text",
        transport=httpx.MockTransport(handler),
    )


async def _collect(agen):
    return [item async for item in agen]


def test_chat_stream_yields_tokens():
    def handler(request):
        body = json.loads(request.content)
        assert request.url.path == "/api/chat"
        assert body["model"] == "gemma2:2b"
        assert body["stream"] is True
        lines = [
            {"message": {"content": "Hel"}, "done": False},
            {"message": {"content": "lo"}, "done": False},
            {"message": {"content": ""}, "done": True},
        ]
        return httpx.Response(200, content="\n".join(json.dumps(line) for line in lines))

    client = make_client(handler)
    tokens = asyncio.run(_collect(client.chat_stream([{"role": "user", "content": "hi"}])))
    assert tokens == ["Hel", "lo"]


def test_chat_stream_missing_model_raises():
    def handler(request):
        return httpx.Response(404, json={"error": "model 'gemma2:2b' not found"})

    client = make_client(handler)
    with pytest.raises(OllamaError, match="not found"):
        asyncio.run(_collect(client.chat_stream([{"role": "user", "content": "hi"}])))


def test_chat_stream_connection_error_raises():
    def handler(request):
        raise httpx.ConnectError("connection refused")

    client = make_client(handler)
    with pytest.raises(OllamaError):
        asyncio.run(_collect(client.chat_stream([{"role": "user", "content": "hi"}])))


def test_chat_stream_error_line_raises():
    def handler(request):
        return httpx.Response(200, content=json.dumps({"error": "out of memory"}))

    client = make_client(handler)
    with pytest.raises(OllamaError, match="out of memory"):
        asyncio.run(_collect(client.chat_stream([{"role": "user", "content": "hi"}])))


def test_embed_returns_vectors():
    def handler(request):
        body = json.loads(request.content)
        assert request.url.path == "/api/embed"
        assert body == {"model": "nomic-embed-text", "input": ["a", "b"]}
        return httpx.Response(200, json={"embeddings": [[0.1, 0.2], [0.3, 0.4]]})

    client = make_client(handler)
    assert asyncio.run(client.embed(["a", "b"])) == [[0.1, 0.2], [0.3, 0.4]]


def test_embed_http_error_raises():
    def handler(request):
        return httpx.Response(500, text="boom")

    client = make_client(handler)
    with pytest.raises(OllamaError, match="500"):
        asyncio.run(client.embed(["a"]))


def test_list_models():
    def handler(request):
        assert request.url.path == "/api/tags"
        return httpx.Response(
            200, json={"models": [{"name": "gemma2:2b"}, {"name": "nomic-embed-text:latest"}]}
        )

    client = make_client(handler)
    assert asyncio.run(client.list_models()) == ["gemma2:2b", "nomic-embed-text:latest"]
