"""Build the Chroma index from backend/knowledge/**/*.md. Run: python -m app.services.ingest"""

import asyncio
import re
from pathlib import Path

from app.core.config import get_settings
from app.services.ollama import OllamaClient
from app.services.rag import Embedder, reset_collection

DOC_PREFIX = "search_document: "
MAX_CHUNK_CHARS = 1500
BATCH_SIZE = 16


def _split_long(body: str) -> list[str]:
    if len(body) <= MAX_CHUNK_CHARS:
        return [body]
    pieces, current = [], ""
    for para in re.split(r"\n\s*\n", body):
        candidate = f"{current}\n\n{para}" if current else para
        if len(candidate) <= MAX_CHUNK_CHARS:
            current = candidate
        else:
            if current:
                pieces.append(current)
            current = para
    if current:
        pieces.append(current)
    return pieces


def split_markdown(text: str, source: str) -> list[dict]:
    lines = text.splitlines()
    title = Path(source).stem
    if lines and lines[0].startswith("# "):
        title, lines = lines[0][2:].strip(), lines[1:]

    sections, heading, body = [], title, []
    for line in lines:
        if line.startswith("## "):
            sections.append((heading, body))
            heading, body = line[3:].strip(), []
        else:
            body.append(line)
    sections.append((heading, body))

    chunks = []
    for heading, body_lines in sections:
        body_text = "\n".join(body_lines).strip()
        if not body_text:
            continue
        for piece in _split_long(body_text):
            chunks.append(
                {"text": f"{title} — {heading}\n\n{piece}", "source": source, "heading": heading}
            )
    return chunks


async def ingest(knowledge_dir: Path, chroma_path: Path, embed: Embedder) -> int:
    chunks = []
    for path in sorted(Path(knowledge_dir).rglob("*.md")):
        source = path.relative_to(knowledge_dir).as_posix()
        chunks.extend(split_markdown(path.read_text(encoding="utf-8"), source))

    collection = reset_collection(Path(chroma_path))
    for start in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[start : start + BATCH_SIZE]
        vectors = await embed([DOC_PREFIX + c["text"] for c in batch])
        collection.add(
            ids=[f"{c['source']}#{start + i}" for i, c in enumerate(batch)],
            embeddings=vectors,
            documents=[c["text"] for c in batch],
            metadatas=[{"source": c["source"], "heading": c["heading"]} for c in batch],
        )
    return collection.count()


async def _run() -> int:
    settings = get_settings()
    client = OllamaClient(settings.ollama_url, settings.chat_model, settings.embed_model)
    try:
        return await ingest(
            settings.resolve(settings.knowledge_path),
            settings.resolve(settings.chroma_path),
            client.embed,
        )
    finally:
        await client.aclose()


def main() -> None:
    count = asyncio.run(_run())
    print(f"Indexed {count} knowledge chunks.")


if __name__ == "__main__":
    main()
