from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from urllib.parse import urlsplit, urlunsplit


@dataclass(frozen=True)
class GoldReconciliation:
    historical_expected: int
    live_count: int
    accepted_count: int
    status: str
    reason: str


def _canonical_key(url: str) -> str:
    p = urlsplit(url)
    return urlunsplit((p.scheme, p.netloc, p.path, "", ""))


def reconcile_gold(historical_expected: int, items, start: date, end: date) -> GoldReconciliation:
    """Use official live evidence as authority; historical Gold is reference only."""
    keys: set[str] = set()
    invalid: list[str] = []
    for item in items:
        parsed = urlsplit(item.detail_url)
        key = _canonical_key(item.detail_url)
        if parsed.scheme != "https" or parsed.netloc != "www.seaisi.org":
            invalid.append(f"{item.article_id or item.title}:NON_SEAISI")
        if not (start <= item.published_date <= end):
            invalid.append(f"{item.article_id or item.title}:OUT_OF_SCOPE")
        if not item.title.strip():
            invalid.append(f"{item.article_id or item.title}:INVALID_TITLE")
        if item.read_status != "READ_OK":
            invalid.append(f"{item.article_id or item.title}:BODY_NOT_READ_OK")
        if key in keys:
            invalid.append(f"{item.article_id or item.title}:CANONICAL_DUPLICATE")
        keys.add(key)
    if invalid:
        return GoldReconciliation(historical_expected, len(items), 0, "GOLD_DIVERGENCE_UNRESOLVED", ";".join(invalid))
    if len(items) == historical_expected:
        return GoldReconciliation(historical_expected, len(items), len(items), "GOLD_MATCH", "official live evidence matches historical reference")
    if len(items) > historical_expected:
        return GoldReconciliation(historical_expected, len(items), len(items), "PASS_WITH_GOLD_CORRECTION", f"official live evidence corrected Gold {historical_expected} → {len(items)}")
    return GoldReconciliation(historical_expected, len(items), 0, "GOLD_DIVERGENCE_UNRESOLVED", f"live inventory {len(items)} is below historical reference {historical_expected} and has no resolving official evidence")
