import asyncio

from app.services.ingest import DOC_PREFIX, MAX_CHUNK_CHARS, ingest, split_markdown
from app.services.rag import open_collection

DOC = (
    "# Wi-Fi Troubleshooting\n\nIntro text.\n\n"
    "## Restart the router\n\nUnplug it.\n\n"
    "## Forget the network\n\nOpen settings.\n"
)


def test_split_by_heading():
    chunks = split_markdown(DOC, "networking/wifi.md")
    assert [c["heading"] for c in chunks] == [
        "Wi-Fi Troubleshooting",
        "Restart the router",
        "Forget the network",
    ]
    assert chunks[1]["text"] == "Wi-Fi Troubleshooting — Restart the router\n\nUnplug it."
    assert all(c["source"] == "networking/wifi.md" for c in chunks)


def test_long_section_split_on_paragraphs():
    para = "x" * 900
    chunks = split_markdown(f"# T\n\n## Big\n\n{para}\n\n{para}", "a/b.md")
    assert len(chunks) == 2
    prefix_len = len("T — Big\n\n")
    assert all(len(c["text"]) <= MAX_CHUNK_CHARS + prefix_len for c in chunks)


def test_title_falls_back_to_file_name():
    chunks = split_markdown("## Only\n\nBody", "software/email-setup.md")
    assert chunks == [
        {"text": "email-setup — Only\n\nBody", "source": "software/email-setup.md", "heading": "Only"}
    ]


def test_empty_sections_skipped():
    chunks = split_markdown("# T\n\n## Empty\n\n## Real\n\nBody", "a/b.md")
    assert [c["heading"] for c in chunks] == ["Real"]


def test_ingest_builds_collection_idempotently(tmp_path):
    knowledge = tmp_path / "knowledge"
    (knowledge / "networking").mkdir(parents=True)
    (knowledge / "networking" / "wifi.md").write_text(DOC, encoding="utf-8")
    (knowledge / "software").mkdir()
    (knowledge / "software" / "email.md").write_text("# Email\n\n## Setup\n\nAdd account.", encoding="utf-8")
    chroma = tmp_path / "chroma"

    async def fake_embed(texts):
        assert all(t.startswith(DOC_PREFIX) for t in texts)
        return [[1.0, 0.5, float(len(t))] for t in texts]

    assert asyncio.run(ingest(knowledge, chroma, fake_embed)) == 4
    assert asyncio.run(ingest(knowledge, chroma, fake_embed)) == 4
    sources = {m["source"] for m in open_collection(chroma).get()["metadatas"]}
    assert sources == {"networking/wifi.md", "software/email.md"}
