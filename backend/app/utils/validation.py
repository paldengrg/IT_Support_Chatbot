from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.chat import ChatTurn

MAX_MESSAGE_CHARS = 2000
MAX_HISTORY_TURNS = 10


def clean_message(message: str) -> str:
    cleaned = message.strip()
    if not cleaned:
        raise ValueError("Message must not be empty.")
    if len(cleaned) > MAX_MESSAGE_CHARS:
        raise ValueError(f"Message must be at most {MAX_MESSAGE_CHARS} characters.")
    return cleaned


def trim_history(history: list[ChatTurn]) -> list[ChatTurn]:
    non_blank = [turn for turn in history if turn.content.strip()]
    return non_blank[-MAX_HISTORY_TURNS:]
