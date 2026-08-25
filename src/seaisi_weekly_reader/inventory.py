from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class InventoryItem:
    published_date: date
    title: str
    detail_url: str
    read_status: str


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

        if not item.detail_url.startswith("https://www.seaisi.org/"):
            raise ValueError(f"non-SEAISI detail URL: {item.detail_url}")

        if item.read_status not in VALID_READ_STATUSES:
            raise ValueError(f"invalid read status: {item.read_status}")

        if item.detail_url in seen_urls:
            raise ValueError(f"duplicate detail URL: {item.detail_url}")

        seen_urls.add(item.detail_url)
