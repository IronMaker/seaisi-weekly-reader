from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from urllib.parse import urlsplit, urlunsplit


@dataclass(frozen=True)
class InventoryItem:
    published_date: date
    title: str
    detail_url: str
    read_status: str
    article_id: str = ""
    category: str = ""
    source_route: str = ""


VALID_READ_STATUSES = {
    "PENDING",
    "READ_OK",
    "RETRY_REQUIRED",
    "FAILED",
}


def validate_inventory(items: list[InventoryItem]) -> None:
    seen_urls: set[str] = set()

    for item in items:
        if not item.title.strip():
            raise ValueError("inventory item title is empty")

        parsed = urlsplit(item.detail_url)
        if parsed.scheme != "https" or parsed.netloc != "www.seaisi.org":
            raise ValueError(f"non-SEAISI detail URL: {item.detail_url}")
        if not parsed.path.startswith("/details/"):
            raise ValueError(f"non-canonical SEAISI detail URL: {item.detail_url}")

        if item.read_status not in VALID_READ_STATUSES:
            raise ValueError(f"invalid read status: {item.read_status}")

        canonical_url = urlunsplit((parsed.scheme, parsed.netloc, parsed.path, "", ""))
        if canonical_url in seen_urls:
            raise ValueError(f"duplicate detail URL: {item.detail_url}")

        seen_urls.add(canonical_url)
