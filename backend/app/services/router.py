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
    r"\b(windows|mac|macs|macos|macbook|imac|linux|ubuntu|debian|fedora|computers?|laptops?"
    r"|desktops?|pcs?|printers?|printing|print|scanners?|wi-?fi|wireless|internet|networks?"
    r"|networking|ethernet|routers?|modems?|vpn|e-?mails?|outlook|gmail|inbox|passwords?"
    r"|passcodes?|login|log in|sign in|signin|accounts?|mfa|2fa|install|installs|installed"
    r"|installing|installation|uninstall|uninstalled|reinstall|reinstalled|software|apps?"
    r"|applications?|programs?|update|updates|updated|upgrade|upgrades|drivers?|errors?"
    r"|crash|crashes|crashed|crashing|freeze|freezes|freezing|froze|frozen|screens?|display"
    r"|monitors?|keyboards?|mouse|bluetooth|usb|microsoft|office|excel|powerpoint|teams|zoom"
    r"|slack|sharepoint|adobe|acrobat|pdf|browsers?|chrome|firefox|edge|safari|disk|storage"
    r"|ram|cpu|slow|boot|restart|reboot|virus|antivirus|backups?|files?|folders?|onedrive"
    r"|dropbox|servers?|dns|ip|sync|syncing|synced|phones?|iphone|android|ipad|tablets?"
    r"|webcam|camera|microphone|mic|headset|headphones|speakers?|audio|sound)\b"
)

_OFF_TOPIC_RE = re.compile(
    r"\b(recipes?|cook|cooking|bake|baking|pizza|food|restaurant|poems?|poetry|story|stories"
    r"|song|lyrics|jokes?|weather|football|soccer|cricket|basketball|world cup|sports?"
    r"|movies?|films?|celebrity|celebrities|capital of|history|homework|essay|dating"
    r"|relationship|girlfriend|boyfriend|medical|doctor|symptoms?|diet|workout|stocks?"
    r"|invest|investing|crypto|bitcoin|horoscope|travel|holiday|vacation|politics|election)\b"
)

# Licensing nouns mark a message as in scope even when it also contains an off-topic word.
_LICENSE_NOUN_RE = re.compile(
    r"\b(licen[cs]es?|licen[cs]ed|licen[cs]ing|(product|license|licence|activation|serial) key"
    r"|serial number|subscriptions?)\b"
)
_LICENSE_RE = re.compile(
    rf"{_LICENSE_NOUN_RE.pattern}"
    r"|\b(renew|renewal|renewing|price|prices|pricing|cost|costs|buy|buying|purchase|purchasing)\b"
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
    in_scope = bool(_IT_RE.search(text) or _LICENSE_NOUN_RE.search(text))
    if not in_scope and _OFF_TOPIC_RE.search(text):
        return Intent.OUT_OF_SCOPE
    if _LICENSE_RE.search(text):
        return Intent.LICENSE
    return Intent.IT_SUPPORT
