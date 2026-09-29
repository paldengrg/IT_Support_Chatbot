"""Rebuild the knowledge-base index. Usage (from repo root or backend/):
    backend/.venv/Scripts/python scripts/ingest_knowledge.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.services.ingest import main  # noqa: E402

if __name__ == "__main__":
    main()
