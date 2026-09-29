# IT Support Chatbot

A local IT Support Assistant (ITEC 320). It answers IT troubleshooting, software, networking, account and licensing questions using a company knowledge base, and politely declines anything else.

- **Backend:** Python, FastAPI, Ollama (`gemma2:2b`), ChromaDB RAG with `nomic-embed-text` embeddings
- **Frontend:** Next.js (App Router)

## How it works

1. A keyword router classifies each message: greetings and clearly off-topic requests get fixed replies without calling the model.
2. IT and license questions retrieve the closest knowledge-base passages from ChromaDB.
3. License questions also include matching entries from `backend/data/licenses.json` (fictional sample data).
4. Gemma answers, streamed to the browser, with the knowledge-base sources listed under the answer.

## Prerequisites

- [Ollama](https://ollama.com) running locally with both models:
  ```
  ollama pull gemma2:2b
  ollama pull nomic-embed-text
  ```
- Python 3.12+ and Node.js 20+

## Run locally

Backend (from `backend/`):
```
py -3 -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
copy .env.example .env
.venv/Scripts/python ../scripts/ingest_knowledge.py
.venv/Scripts/python -m uvicorn app.main:app --reload
```
(macOS/Linux: use `python3 -m venv .venv`, `.venv/bin/python`, and `cp`.)

Frontend (from `frontend/`):
```
npm install
npm run dev
```

Open http://localhost:3000. Health check: http://localhost:8000/api/health

## Run with Docker

With Ollama running on the host:
```
docker compose up --build
```

## Updating the knowledge base

Add or edit Markdown files under `backend/knowledge/<topic>/`. Use `# Title` and `## Section` headings; each section becomes a searchable chunk. Then re-run `scripts/ingest_knowledge.py` and restart the backend.

## Tests

From `backend/`:
```
.venv/Scripts/python -m pytest -v
```
`tests/test_integration_ollama.py` runs only when Ollama is reachable.

## Configuration

`backend/.env` (see `.env.example`): Ollama URL, model names, Chroma path, `RAG_TOP_K`, `RAG_MAX_DISTANCE`, `FRONTEND_ORIGIN`. Frontend: `NEXT_PUBLIC_API_URL` in `frontend/.env.local`.

## Project structure

```
backend/app/api        chat + health endpoints
backend/app/core       settings and system prompt
backend/app/services   router, RAG, ingestion, Ollama client, licenses
backend/knowledge      knowledge-base articles (Markdown)
backend/data           licenses.json (sample data)
frontend/              Next.js chat UI
scripts/               ingest_knowledge.py
```
