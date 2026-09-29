from fastapi.testclient import TestClient

from app.api.deps import get_kb, get_ollama
from app.main import create_app
from app.services.ollama import OllamaError


class FakeOllama:
    chat_model = "gemma2:2b"
    embed_model = "nomic-embed-text"

    def __init__(self, models=("gemma2:2b", "nomic-embed-text:latest"), down=False):
        self.models = list(models)
        self.down = down

    async def list_models(self):
        if self.down:
            raise OllamaError("down")
        return self.models


class FakeKB:
    def __init__(self, count=10):
        self._count = count

    def count(self):
        return self._count


def get_health(ollama, kb):
    app = create_app()
    app.dependency_overrides[get_ollama] = lambda: ollama
    app.dependency_overrides[get_kb] = lambda: kb
    return TestClient(app).get("/api/health").json()


def test_health_ok():
    assert get_health(FakeOllama(), FakeKB()) == {
        "status": "ok",
        "ollama": True,
        "models": ["gemma2:2b", "nomic-embed-text:latest"],
        "kb_chunks": 10,
    }


def test_health_degraded_when_kb_empty():
    assert get_health(FakeOllama(), FakeKB(count=0))["status"] == "degraded"


def test_health_degraded_when_model_missing():
    assert get_health(FakeOllama(models=["nomic-embed-text:latest"]), FakeKB())["status"] == "degraded"


def test_health_degraded_when_ollama_down():
    body = get_health(FakeOllama(down=True), FakeKB())
    assert body["status"] == "degraded"
    assert body["ollama"] is False
    assert body["models"] == []
