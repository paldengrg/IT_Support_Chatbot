import pytest

from app.services.router import Intent, classify, is_thanks


@pytest.mark.parametrize(
    "msg",
    ["hi", "Hello!", "hey there", "Good morning", "thanks", "Thank you!", "thanks a lot", "cheers"],
)
def test_greetings(msg):
    assert classify(msg) is Intent.GREETING


@pytest.mark.parametrize(
    "msg",
    [
        "Write me a poem about the ocean",
        "Who won the World Cup?",
        "What's a good recipe for pizza?",
        "What is the capital of France?",
        "Tell me a joke",
        "What's the weather tomorrow?",
        "Should I invest in bitcoin?",
    ],
)
def test_out_of_scope(msg):
    assert classify(msg) is Intent.OUT_OF_SCOPE


@pytest.mark.parametrize(
    "msg",
    [
        "My Wi-Fi keeps disconnecting on Windows 11",
        "How do I install a printer on my Mac?",
        "I forgot my Outlook password",
        "The VPN won't connect",
        "How do I install Python on Ubuntu?",
        "My laptop is very slow",
    ],
)
def test_it_support(msg):
    assert classify(msg) is Intent.IT_SUPPORT


@pytest.mark.parametrize(
    "msg",
    [
        "How much does a Microsoft 365 license cost?",
        "How do I renew my Adobe subscription?",
        "I need to activate my licence",
        "Can I buy Zoom Pro?",
        "Where do I enter my product key?",
    ],
)
def test_license(msg):
    assert classify(msg) is Intent.LICENSE


@pytest.mark.parametrize(
    "msg",
    [
        "Hi, my printer won't print",
        "Thanks, but the VPN still fails",
        "hello can you help me reset my password",
    ],
)
def test_greeting_with_question_is_not_greeting(msg):
    assert classify(msg) is Intent.IT_SUPPORT


@pytest.mark.parametrize(
    "msg",
    ["The football app won't install on my laptop", "My weather widget crashes on Windows"],
)
def test_off_topic_word_inside_it_question(msg):
    assert classify(msg) is Intent.IT_SUPPORT


@pytest.mark.parametrize("msg", ["It doesn't work", "Can you help me?"])
def test_ambiguous_goes_to_llm(msg):
    assert classify(msg) is Intent.IT_SUPPORT


@pytest.mark.parametrize("msg", ["wifi not working", "WiFi is down", "wi-fi drops"])
def test_wifi_spellings(msg):
    assert classify(msg) is Intent.IT_SUPPORT


@pytest.mark.parametrize(
    "msg",
    [
        "Both printers in the history department are jammed",
        "How do I clear my history in Edge?",
        "Adobe Acrobat won't open my essay PDF",
        "My emails from the sports club aren't syncing",
        "My webcam doesn't work for my doctor appointment",
        "My passwords stopped working after the update",
    ],
)
def test_plural_and_device_terms_count_as_it(msg):
    assert classify(msg) is Intent.IT_SUPPORT


def test_license_noun_beats_off_topic_word():
    assert classify("Renew the Adobe Acrobat license for the travel team") is Intent.LICENSE


def test_account_activation_is_not_licensing():
    assert classify("How do I activate my account?") is Intent.IT_SUPPORT


def test_is_thanks():
    assert is_thanks("Thank you!")
    assert is_thanks("thanks a lot")
    assert not is_thanks("hi")
