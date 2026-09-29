import asyncio

import pytest

from app.services.rag import KnowledgeBase, open_collection


def _populated_collection(path):
    collection = open_collection(path)
    collection.add(
        ids=["a", "b"],
        embeddings=[[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]],
        documents=["wifi doc", "printer doc"],
        metadatas=[
            {"source": "networking/wifi.md", "heading": "Wi-Fi"},
            {"source": "macos/printer.md", "heading": "Printer"},
        ],
    )
    return collection


async def _embed_wifi_query(texts):
    assert texts == ["search_query: wifi drops"]
    return [[1.0, 0.1, 0.0]]


def test_search_returns_only_close_chunks(tmp_path):
    kb = KnowledgeBase(_populated_collection(tmp_path), _embed_wifi_query, top_k=4, max_distance=0.5)
    results = asyncio.run(kb.search("wifi drops"))
    assert [c.source for c in results] == ["networking/wifi.md"]
    assert results[0].text == "wifi doc"
    assert results[0].distance < 0.5


def test_search_respects_top_k(tmp_path):
    kb = KnowledgeBase(_populated_collection(tmp_path), _embed_wifi_query, top_k=1, max_distance=2.0)
    assert len(asyncio.run(kb.search("wifi drops"))) == 1


def test_search_empty_collection_skips_embedding(tmp_path):
    async def must_not_embed(texts):
        pytest.fail("embedder should not be called for an empty knowledge base")

    kb = KnowledgeBase(open_collection(tmp_path), must_not_embed, top_k=4, max_distance=0.5)
    assert asyncio.run(kb.search("anything")) == []
    assert kb.count() == 0
