import json

from fastapi.testclient import TestClient

from app.api.chat import SOURCES_MARKER
from app.api.deps import get_kb, get_licenses, get_ollama
from app.core.prompts import (
    GREETING_REPLY,
    NO_KB_INFO,
    OUT_OF_SCOPE_MESSAGE,
    THANKS_REPLY,
    UNAVAILABLE_MESSAGE,
)
from app.main import create_app
from app.models.chat import Chunk
from app.models.license import License
from app.services.ollama import OllamaError

SAMPLE_LICENSES = [
    License(
        product="Zoom Workplace Pro",
        aliases=["zoom"],
        vendor="Zoom",
        price_per_user_year=160,
        currency="USD",
        available=True,
        requires_approval=False,
        renewal="Annual",
        purchase_process="Request via IT portal.",
    )
]


class FakeOllama:
    chat_model = "gemma2:2b"
    embed_model = "nomic-embed-text"

    def __init__(self, tokens=("Hello", " there"), fail_at=None):
        self.tokens = list(tokens)
        self.fail_at = fail_at
        self.calls = []

    async def chat_stream(self, messages):
        self.calls.append(messages)
        for i, token in enumerate(self.tokens):
            if self.fail_at == i:
                raise OllamaError("boom")
            yield token


class FakeKB:
    def __init__(self, chunks=(), error=None):
        self.chunks = list(chunks)
        self.error = error
        self.queries = []

    def count(self):
        return len(self.chunks)

    async def search(self, query):
        self.queries.append(query)
        if self.error:
            raise self.error
        return self.chunks


def build_client(ollama, kb, licenses=SAMPLE_LICENSES):
    app = create_app()
    app.dependency_overrides[get_ollama] = lambda: ollama
    app.dependency_overrides[get_kb] = lambda: kb
    app.dependency_overrides[get_licenses] = lambda: licenses
    return TestClient(app)


def split_body(body):
    text, marker, trailer = body.partition(SOURCES_MARKER)
    return text, (json.loads(trailer)["sources"] if marker else None)


def post(client, message, history=()):
    return client.post("/api/chat", json={"message": message, "history": list(history)})


def test_greeting_is_canned_and_skips_llm():
    ollama, kb = FakeOllama(), FakeKB()
    resp = post(build_client(ollama, kb), "hi")
    assert resp.status_code == 200
    assert split_body(resp.text) == (GREETING_REPLY, [])
    assert ollama.calls == [] and kb.queries == []


def test_thanks_gets_thanks_reply():
    resp = post(build_client(FakeOllama(), FakeKB()), "Thank you!")
    assert split_body(resp.text) == (THANKS_REPLY, [])


def test_out_of_scope_is_canned_and_skips_llm():
    ollama, kb = FakeOllama(), FakeKB()
    resp = post(build_client(ollama, kb), "Write me a poem about the ocean")
    assert split_body(resp.text) == (OUT_OF_SCOPE_MESSAGE, [])
    assert ollama.calls == [] and kb.queries == []


def test_it_question_streams_answer_with_deduplicated_sources():
    chunks = [
        Chunk(text="Reset adapter", source="networking/wifi.md", distance=0.2),
        Chunk(text="More wifi", source="networking/wifi.md", distance=0.3),
    ]
    ollama = FakeOllama()
    resp = post(build_client(ollama, FakeKB(chunks)), "My wifi drops on Windows")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/plain")
    assert split_body(resp.text) == ("Hello there", ["networking/wifi.md"])
    prompt = ollama.calls[0][-1]["content"]
    assert "Reset adapter" in prompt
    assert "LICENSE DATA" not in prompt


def test_history_is_forwarded_to_model():
    ollama = FakeOllama()
    history = [{"role": "user", "content": "My VPN fails"}, {"role": "assistant", "content": "Which OS?"}]
    post(build_client(ollama, FakeKB()), "Windows 11", history)
    assert ollama.calls[0][1:3] == history


def test_license_question_includes_catalog_data():
    ollama = FakeOllama()
    post(build_client(ollama, FakeKB()), "How much does a Zoom license cost?")
    assert "160 USD per user per year" in ollama.calls[0][-1]["content"]


def test_license_question_without_match_says_no_data():
    ollama = FakeOllama()
    post(build_client(ollama, FakeKB()), "How much does a Photoshop license cost?")
    assert "No matching license data was found." in ollama.calls[0][-1]["content"]


def test_ollama_failure_before_first_token_returns_503():
    resp = post(build_client(FakeOllama(fail_at=0), FakeKB()), "My laptop is slow")
    assert resp.status_code == 503
    assert resp.json() == {"detail": UNAVAILABLE_MESSAGE}


def test_embedding_failure_returns_503():
    resp = post(build_client(FakeOllama(), FakeKB(error=OllamaError("down"))), "My laptop is slow")
    assert resp.status_code == 503


def test_kb_failure_falls_back_to_no_context():
    ollama = FakeOllama()
    resp = post(build_client(ollama, FakeKB(error=RuntimeError("chroma broke"))), "My laptop is slow")
    assert resp.status_code == 200
    assert NO_KB_INFO in ollama.calls[0][-1]["content"]


def test_stream_interrupted_mid_answer_has_no_trailer():
    resp = post(build_client(FakeOllama(fail_at=1), FakeKB()), "My laptop is slow")
    assert resp.status_code == 200
    assert resp.text == "Hello"


def test_invalid_input_returns_422():
    client = build_client(FakeOllama(), FakeKB())
    assert post(client, "   ").status_code == 422
    assert post(client, "a" * 2001).status_code == 422


def test_cors_allows_frontend_origin():
    client = build_client(FakeOllama(), FakeKB())
    resp = client.options(
        "/api/chat",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert resp.headers["access-control-allow-origin"] == "http://localhost:3000"
