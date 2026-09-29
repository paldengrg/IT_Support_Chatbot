import pytest
from pydantic import ValidationError

from app.models.chat import ChatRequest, ChatTurn
from app.utils.validation import MAX_HISTORY_TURNS, MAX_MESSAGE_CHARS, clean_message, trim_history


def test_clean_message_strips_whitespace():
    assert clean_message("  hello  ") == "hello"


@pytest.mark.parametrize("bad", ["", "   ", "\n\t"])
def test_clean_message_rejects_empty(bad):
    with pytest.raises(ValueError, match="empty"):
        clean_message(bad)


def test_clean_message_rejects_too_long():
    with pytest.raises(ValueError, match="2000"):
        clean_message("a" * (MAX_MESSAGE_CHARS + 1))


def test_clean_message_accepts_max_length():
    assert len(clean_message("a" * MAX_MESSAGE_CHARS)) == MAX_MESSAGE_CHARS


def test_trim_history_keeps_last_turns():
    history = [
        ChatTurn(role="user" if i % 2 == 0 else "assistant", content=f"m{i}") for i in range(15)
    ]
    trimmed = trim_history(history)
    assert len(trimmed) == MAX_HISTORY_TURNS
    assert trimmed[0].content == "m5"
    assert trimmed[-1].content == "m14"


def test_trim_history_drops_blank_entries():
    history = [ChatTurn(role="user", content="  "), ChatTurn(role="assistant", content="ok")]
    assert [t.content for t in trim_history(history)] == ["ok"]


def test_chat_request_applies_validation():
    req = ChatRequest(
        message="  help  ",
        history=[ChatTurn(role="user", content=str(i)) for i in range(12)],
    )
    assert req.message == "help"
    assert len(req.history) == 10


def test_chat_request_rejects_bad_role():
    with pytest.raises(ValidationError):
        ChatRequest(message="hi", history=[{"role": "system", "content": "x"}])


def test_chat_request_rejects_empty_message():
    with pytest.raises(ValidationError):
        ChatRequest(message="   ")
