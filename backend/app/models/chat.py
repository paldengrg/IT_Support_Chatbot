from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, field_validator

from app.utils.validation import clean_message, trim_history


class ChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[ChatTurn] = []

    @field_validator("message")
    @classmethod
    def _clean_message(cls, value: str) -> str:
        return clean_message(value)

    @field_validator("history")
    @classmethod
    def _trim_history(cls, value: list[ChatTurn]) -> list[ChatTurn]:
        return trim_history(value)


@dataclass(frozen=True)
class Chunk:
    """A knowledge-base passage returned by retrieval."""

    text: str
    source: str
    distance: float
