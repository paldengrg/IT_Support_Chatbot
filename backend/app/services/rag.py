from collections.abc import Awaitable, Callable
from pathlib import Path

import chromadb

from app.models.chat import Chunk

COLLECTION_NAME = "it_knowledge"
QUERY_PREFIX = "search_query: "
_COSINE = {"hnsw:space": "cosine"}

Embedder = Callable[[list[str]], Awaitable[list[list[float]]]]


def _client(path: Path) -> chromadb.ClientAPI:
    return chromadb.PersistentClient(path=str(path))


def open_collection(path: Path):
    return _client(path).get_or_create_collection(COLLECTION_NAME, metadata=_COSINE)


def reset_collection(path: Path):
    client = _client(path)
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:  # chromadb raises NotFoundError when the collection does not exist
        pass
    return client.create_collection(COLLECTION_NAME, metadata=_COSINE)


class KnowledgeBase:
    def __init__(self, collection, embed: Embedder, top_k: int, max_distance: float) -> None:
        self._collection = collection
        self._embed = embed
        self._top_k = top_k
        self._max_distance = max_distance

    def count(self) -> int:
        return self._collection.count()

    async def search(self, query: str) -> list[Chunk]:
        total = self.count()
        if total == 0:
            return []
        [vector] = await self._embed([QUERY_PREFIX + query])
        result = self._collection.query(
            query_embeddings=[vector], n_results=min(self._top_k, total)
        )
        return [
            Chunk(text=doc, source=meta["source"], distance=dist)
            for doc, meta, dist in zip(
                result["documents"][0], result["metadatas"][0], result["distances"][0]
            )
            if dist <= self._max_distance
        ]
