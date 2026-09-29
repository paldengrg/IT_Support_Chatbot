import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import chat, health
from app.core.config import get_settings
from app.services.license_service import load_licenses
from app.services.ollama import OllamaClient
from app.services.rag import KnowledgeBase, open_collection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    ollama = OllamaClient(settings.ollama_url, settings.chat_model, settings.embed_model)
    kb = KnowledgeBase(
        open_collection(settings.resolve(settings.chroma_path)),
        ollama.embed,
        settings.rag_top_k,
        settings.rag_max_distance,
    )
    if kb.count() == 0:
        logger.warning("Knowledge base is empty. Run: python scripts/ingest_knowledge.py")
    app.state.ollama = ollama
    app.state.kb = kb
    app.state.licenses = load_licenses(settings.resolve(settings.licenses_path))
    yield
    await ollama.aclose()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="IT Support Chatbot", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_origin],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(chat.router)
    app.include_router(health.router)
    return app


app = create_app()
