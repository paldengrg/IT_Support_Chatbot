import json
from collections.abc import AsyncIterator

import httpx


class OllamaError(RuntimeError):
    """Ollama is unreachable, a model is missing, or a request failed."""


class OllamaClient:
    def __init__(
        self,
        base_url: str,
        chat_model: str,
        embed_model: str,
        timeout: float = 120.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.chat_model = chat_model
        self.embed_model = embed_model
        self._client = httpx.AsyncClient(base_url=base_url, timeout=timeout, transport=transport)

    async def aclose(self) -> None:
        await self._client.aclose()

    async def embed(self, texts: list[str]) -> list[list[float]]:
        try:
            resp = await self._client.post(
                "/api/embed", json={"model": self.embed_model, "input": texts}
            )
        except httpx.HTTPError as exc:
            raise OllamaError(f"Cannot reach Ollama: {exc}") from exc
        if resp.status_code != 200:
            raise OllamaError(f"Ollama embed failed ({resp.status_code}): {resp.text}")
        return resp.json()["embeddings"]

    async def chat_stream(self, messages: list[dict[str, str]]) -> AsyncIterator[str]:
        payload = {
            "model": self.chat_model,
            "messages": messages,
            "stream": True,
            "options": {"temperature": 0.2},
        }
        try:
            async with self._client.stream("POST", "/api/chat", json=payload) as resp:
                if resp.status_code != 200:
                    body = (await resp.aread()).decode(errors="replace")
                    raise OllamaError(f"Ollama chat failed ({resp.status_code}): {body}")
                async for line in resp.aiter_lines():
                    if not line.strip():
                        continue
                    data = json.loads(line)
                    if "error" in data:
                        raise OllamaError(data["error"])
                    content = data.get("message", {}).get("content", "")
                    if content:
                        yield content
                    if data.get("done"):
                        break
        except httpx.HTTPError as exc:
            raise OllamaError(f"Cannot reach Ollama: {exc}") from exc

    async def list_models(self) -> list[str]:
        try:
            resp = await self._client.get("/api/tags")
        except httpx.HTTPError as exc:
            raise OllamaError(f"Cannot reach Ollama: {exc}") from exc
        if resp.status_code != 200:
            raise OllamaError(f"Ollama tags failed ({resp.status_code})")
        return [model["name"] for model in resp.json().get("models", [])]
