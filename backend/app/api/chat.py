import json
import logging
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.api.deps import get_kb, get_licenses, get_ollama
from app.core.prompts import (
    GREETING_REPLY,
    OUT_OF_SCOPE_MESSAGE,
    THANKS_REPLY,
    UNAVAILABLE_MESSAGE,
    build_messages,
)
from app.models.chat import ChatRequest
from app.models.license import License
from app.services.license_service import find_licenses, format_license_block
from app.services.ollama import OllamaClient, OllamaError
from app.services.rag import KnowledgeBase
from app.services.router import Intent, classify, is_thanks

SOURCES_MARKER = "\n[[SOURCES]]"

logger = logging.getLogger(__name__)
router = APIRouter()


def _trailer(sources: list[str]) -> str:
    return SOURCES_MARKER + json.dumps({"sources": sources})


def _stream(body: AsyncIterator[str]) -> StreamingResponse:
    return StreamingResponse(body, media_type="text/plain; charset=utf-8")


async def _canned(text: str) -> AsyncIterator[str]:
    yield text
    yield _trailer([])


@router.post("/api/chat")
async def chat(
    req: ChatRequest,
    ollama: OllamaClient = Depends(get_ollama),
    kb: KnowledgeBase = Depends(get_kb),
    licenses: list[License] = Depends(get_licenses),
) -> StreamingResponse:
    intent = classify(req.message)
    if intent is Intent.GREETING:
        return _stream(_canned(THANKS_REPLY if is_thanks(req.message) else GREETING_REPLY))
    if intent is Intent.OUT_OF_SCOPE:
        return _stream(_canned(OUT_OF_SCOPE_MESSAGE))

    try:
        chunks = await kb.search(req.message)
    except OllamaError as exc:
        logger.error("Embedding failed: %s", exc)
        raise HTTPException(status_code=503, detail=UNAVAILABLE_MESSAGE) from exc
    except Exception:
        logger.exception("Knowledge base search failed; answering without context")
        chunks = []

    license_block = None
    if intent is Intent.LICENSE:
        license_block = format_license_block(find_licenses(req.message, licenses))

    tokens = ollama.chat_stream(build_messages(req.message, req.history, chunks, license_block))
    try:
        first = await anext(tokens)
    except StopAsyncIteration:
        first = ""
    except OllamaError as exc:
        logger.error("Chat generation failed: %s", exc)
        raise HTTPException(status_code=503, detail=UNAVAILABLE_MESSAGE) from exc

    sources = list(dict.fromkeys(chunk.source for chunk in chunks))

    async def body() -> AsyncIterator[str]:
        yield first
        try:
            async for token in tokens:
                yield token
        except OllamaError as exc:
            # No trailer: the client treats a missing trailer as an interrupted response.
            logger.error("Chat stream interrupted: %s", exc)
            return
        yield _trailer(sources)

    return _stream(body())
