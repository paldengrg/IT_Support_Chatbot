"""Deterministic intent routing so greetings and off-topic requests never reach the LLM."""

import re
from enum import Enum


class Intent(str, Enum):
    GREETING = "greeting"
    OUT_OF_SCOPE = "out_of_scope"
    LICENSE = "license"
    IT_SUPPORT = "it_support"


_GREETING_RE = re.compile(
    r"^(hi|hello|hey|hiya|howdy|greetings|good (morning|afternoon|evening|day))"
    r"( there| team| everyone)?$"
)
_THANKS_RE = re.compile(
    r"^(thanks|thank you|thank you so much|thanks a lot|thanks so much|many thanks"
    r"|cheers|ok thanks|okay thanks|ty)( very much)?$"
)

_IT_RE = re.compile(
    r"\b(windows|mac|macos|macbook|imac|linux|ubuntu|debian|fedora|computer|laptop|desktop|pc"
    r"|printer|printing|print|scanner|wi-?fi|wireless|internet|network|ethernet|router|modem|vpn"
    r"|email|e-mail|outlook|gmail|inbox|password|passcode|login|log in|sign in|signin|account"
    r"|mfa|2fa|install|installing|installation|uninstall|reinstall|software|app|apps"
    r"|application|program|update|updates|upgrade|driver|drivers|error|crash|crashes|crashing"
    r"|freeze|frozen|screen|display|monitor|keyboard|mouse|bluetooth|usb|microsoft|office"
    r"|excel|powerpoint|teams|zoom|browser|chrome|firefox|safari|disk|storage|ram|cpu|slow"
    r"|boot|restart|reboot|virus|antivirus|backup|file|files|folder|onedrive|dropbox|server"
    r"|dns|ip)\b"
)

_OFF_TOPIC_RE = re.compile(
    r"\b(recipes?|cook|cooking|bake|baking|pizza|food|restaurant|poems?|poetry|story|stories"
    r"|song|lyrics|jokes?|weather|football|soccer|cricket|basketball|world cup|sports?"
    r"|movies?|films?|celebrity|celebrities|capital of|history|homework|essay|dating"
    r"|relationship|girlfriend|boyfriend|medical|doctor|symptoms?|diet|workout|stocks?"
    r"|invest|investing|crypto|bitcoin|horoscope|travel|holiday|vacation|politics|election)\b"
)

_LICENSE_RE = re.compile(
    r"\b(licen[cs]es?|licen[cs]ed|licen[cs]ing|product key|serial (key|number)|activation"
    r"|activate|activating|renew|renewal|renewing|subscriptions?|price|prices|pricing|cost"
    r"|costs|buy|buying|purchase|purchasing)\b"
)


def _normalize(message: str) -> str:
    text = re.sub(r"[^a-z0-9'\s-]", " ", message.lower())
    return " ".join(text.split())


def is_thanks(message: str) -> bool:
    return bool(_THANKS_RE.match(_normalize(message)))


def classify(message: str) -> Intent:
    text = _normalize(message)
    if _GREETING_RE.match(text) or _THANKS_RE.match(text):
        return Intent.GREETING
    has_it_terms = bool(_IT_RE.search(text))
    if not has_it_terms and _OFF_TOPIC_RE.search(text):
        return Intent.OUT_OF_SCOPE
    if _LICENSE_RE.search(text):
        return Intent.LICENSE
    return Intent.IT_SUPPORT
