from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable


class RetrievalIncomplete(RuntimeError):
    pass


@dataclass
class RetrievalRecord:
    detail_url: str
    title: str
    status: str = "PENDING"
    body: str = ""
    attempts: list[dict[str, str]] = field(default_factory=list)
    external_source_substitution: bool = False


def retrieve_official(item, fetch: Callable[[str], tuple[int, str, str]], exact_title_search=None, equivalent_url=None):
    """Retrieve an article from SEAISI only, with at most three official attempts."""
    urls = [item.detail_url]
    if exact_title_search:
        urls.append(exact_title_search(item.title))
    if equivalent_url:
        urls.append(equivalent_url(item))
    record = RetrievalRecord(item.detail_url, item.title)
    seen = set()
    for attempt, url in enumerate(urls[:3], 1):
        if not url or url in seen:
            continue
        seen.add(url)
        try:
            status, body, final_url = fetch(url)
            readable = status == 200 and bool(body.strip()) and final_url.startswith("https://www.seaisi.org/")
            record.attempts.append({"round": str(attempt), "url": url, "http_status": str(status), "final_url": final_url, "readable": str(readable)})
            if readable:
                record.status, record.body = "READ_OK", body
                return record
        except Exception as exc:
            record.attempts.append({"round": str(attempt), "url": url, "error": type(exc).__name__ + ": " + str(exc)})
    record.status = "FAILED"
    return record


def completeness_gate(read_statuses: list[str]) -> None:
    """
    Formal report generation is allowed only when every frozen inventory item
    has successfully retrieved official SEAISI body content.
    """
    failed = [status for status in read_statuses if status != "READ_OK"]

    if failed:
        raise RetrievalIncomplete(
            f"{len(failed)} inventory item(s) are not READ_OK"
        )
