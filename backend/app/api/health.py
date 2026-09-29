from fastapi import APIRouter, Depends

from app.api.deps import get_kb, get_ollama
from app.services.ollama import OllamaClient, OllamaError
from app.services.rag import KnowledgeBase

router = APIRouter()


def _has_model(available: list[str], name: str) -> bool:
    return any(model in (name, f"{name}:latest") for model in available)


@router.get("/api/health")
async def health(
    ollama: OllamaClient = Depends(get_ollama),
    kb: KnowledgeBase = Depends(get_kb),
) -> dict:
    try:
        models, ollama_up = await ollama.list_models(), True
    except OllamaError:
        models, ollama_up = [], False
    try:
        kb_chunks = kb.count()
    except Exception:
        kb_chunks = 0
    ready = (
        ollama_up
        and _has_model(models, ollama.chat_model)
        and _has_model(models, ollama.embed_model)
        and kb_chunks > 0
    )
    return {
        "status": "ok" if ready else "degraded",
        "ollama": ollama_up,
        "models": models,
        "kb_chunks": kb_chunks,
    }
