from app.core.prompts import (
    NO_KB_INFO,
    OUT_OF_SCOPE_MESSAGE,
    SYSTEM_PROMPT,
    build_messages,
)
from app.models.chat import ChatTurn, Chunk


def test_system_prompt_contains_key_rules():
    assert SYSTEM_PROMPT.startswith("You are an IT Support Assistant for an IT company.")
    assert "You are NOT a general-purpose assistant." in SYSTEM_PROMPT
    assert "Never invent license keys." in SYSTEM_PROMPT
    assert "support@example.com" in SYSTEM_PROMPT


def test_out_of_scope_message_is_verbatim():
    assert OUT_OF_SCOPE_MESSAGE == (
        "I'm designed to help with IT support, software installation,\n"
        "troubleshooting, and software licensing.\n\n"
        "For assistance with other requests, please contact IT Support:\n\n"
        "support@example.com"
    )


def test_build_messages_structure():
    chunks = [Chunk(text="Reset adapter steps", source="windows/network.md", distance=0.2)]
    history = [ChatTurn(role="user", content="hi"), ChatTurn(role="assistant", content="Hello!")]
    msgs = build_messages("wifi broken", history, chunks, None)
    assert msgs[0] == {"role": "system", "content": SYSTEM_PROMPT}
    assert msgs[1:3] == [
        {"role": "user", "content": "hi"},
        {"role": "assistant", "content": "Hello!"},
    ]
    last = msgs[-1]
    assert last["role"] == "user"
    assert last["content"].startswith("KNOWLEDGE BASE INFORMATION:")
    assert "[windows/network.md]\nReset adapter steps" in last["content"]
    assert last["content"].endswith("USER QUESTION:\nwifi broken")
    assert "LICENSE DATA" not in last["content"]


def test_build_messages_without_chunks_says_so():
    last = build_messages("wifi broken", [], [], None)[-1]["content"]
    assert NO_KB_INFO in last


def test_build_messages_includes_license_block_before_question():
    last = build_messages("zoom price?", [], [], "LICENSE DATA:\nZoom 160 USD")[-1]["content"]
    assert last.index("LICENSE DATA") < last.index("USER QUESTION:")
