import json
import re
from pathlib import Path

from app.models.license import License

NO_LICENSE_DATA = "LICENSE DATA:\nNo matching license data was found."


def load_licenses(path: Path) -> list[License]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return [License.model_validate(item) for item in data["licenses"]]


def _mentions(term: str, text: str) -> bool:
    return re.search(rf"\b{re.escape(term.lower())}\b", text) is not None


def find_licenses(message: str, licenses: list[License]) -> list[License]:
    text = message.lower()
    return [
        lic
        for lic in licenses
        if any(_mentions(term, text) for term in [lic.product, *lic.aliases])
    ]


def _yes_no(value: bool) -> str:
    return "Yes" if value else "No"


def format_license_block(matches: list[License]) -> str:
    if not matches:
        return NO_LICENSE_DATA
    lines = ["LICENSE DATA (from company records):"]
    for lic in matches:
        lines += [
            f"- Product: {lic.product} ({lic.vendor})",
            f"  Price: {lic.price_per_user_year:g} {lic.currency} per user per year",
            f"  Available: {_yes_no(lic.available)}",
            f"  Requires approval: {_yes_no(lic.requires_approval)}",
            f"  Renewal: {lic.renewal}",
            f"  How to purchase: {lic.purchase_process}",
        ]
    return "\n".join(lines)
