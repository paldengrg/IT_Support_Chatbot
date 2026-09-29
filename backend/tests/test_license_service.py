from app.core.config import BACKEND_DIR
from app.models.license import License
from app.services.license_service import (
    NO_LICENSE_DATA,
    find_licenses,
    format_license_block,
    load_licenses,
)


def _lic(product, aliases, available=True, requires_approval=True, price=100):
    return License(
        product=product,
        aliases=aliases,
        vendor="Vendor",
        price_per_user_year=price,
        currency="USD",
        available=available,
        requires_approval=requires_approval,
        renewal="Annual",
        purchase_process="Request via IT portal.",
    )


CATALOG = [
    _lic("Microsoft 365 Business Standard", ["m365", "office"], price=150),
    _lic("Zoom Workplace Pro", ["zoom"], requires_approval=False, price=160),
    _lic("Autodesk AutoCAD", ["autocad"], available=False, price=2030),
]


def test_load_real_license_file():
    licenses = load_licenses(BACKEND_DIR / "data" / "licenses.json")
    assert len(licenses) >= 5
    assert any(not lic.available for lic in licenses)


def test_find_by_product_name():
    assert [l.product for l in find_licenses("Price of Zoom Workplace Pro?", CATALOG)] == [
        "Zoom Workplace Pro"
    ]


def test_find_by_alias_case_insensitive():
    assert [l.product for l in find_licenses("How much is M365?", CATALOG)] == [
        "Microsoft 365 Business Standard"
    ]


def test_alias_requires_word_boundary():
    assert find_licenses("I zoomed in on the licence page", CATALOG) == []


def test_each_product_returned_once():
    matches = find_licenses("office m365 Microsoft 365 Business Standard", CATALOG)
    assert len(matches) == 1


def test_no_match_returns_empty():
    assert find_licenses("How much does Photoshop cost?", CATALOG) == []


def test_format_block_contains_facts():
    block = format_license_block([CATALOG[1]])
    assert block.startswith("LICENSE DATA (from company records):")
    assert "Zoom Workplace Pro" in block
    assert "160 USD per user per year" in block
    assert "Requires approval: No" in block
    assert "Available: Yes" in block


def test_unavailable_product_is_reported():
    assert "Available: No" in format_license_block([CATALOG[2]])


def test_format_block_no_match():
    assert format_license_block([]) == NO_LICENSE_DATA
