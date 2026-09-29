from fastapi import Request

from app.models.license import License
from app.services.ollama import OllamaClient
from app.services.rag import KnowledgeBase


def get_ollama(request: Request) -> OllamaClient:
    return request.app.state.ollama


def get_kb(request: Request) -> KnowledgeBase:
    return request.app.state.kb


def get_licenses(request: Request) -> list[License]:
    return request.app.state.licenses
