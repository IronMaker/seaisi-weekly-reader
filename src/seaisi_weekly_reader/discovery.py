from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from urllib.parse import urlencode

from .http_client import OfficialHttpClient
from .parser import ListedArticle, parse_listing

LIVE_ROUTE = "https://www.seaisi.org/news-rooms"
CATEGORY_TYPES = (7, 8, 9, 10, 11)


@dataclass
class DiscoveryResult:
    items: list[ListedArticle]
    routes: list[str]
    page_count: int
    frontier_witnesses: list[dict[str, str]]
    exceptions: list[str]


def discover(start: date, end: date, client: OfficialHttpClient) -> DiscoveryResult:
    collected: list[ListedArticle] = []
    routes: list[str] = []
    witnesses: list[dict[str, str]] = []
    exceptions: list[str] = []
    page = 1
    while page <= 20:
        route = LIVE_ROUTE if page == 1 else f"{LIVE_ROUTE}?page={page}"
        status, body, _ = client.get(route)
        routes.append(route)
        if status != 200 or not body:
            exceptions.append(f"LIVE_ROUTE_UNAVAILABLE:{route}:HTTP_{status}")
            break
        listed = parse_listing(body, route)
        if not listed: break
        collected.extend(listed)
        dates = [x.published_date for x in listed]
        if max(dates) > end and not any(x.get("role") == "after_end_frontier" for x in witnesses):
            first_after = min((x for x in listed if x.published_date > end), key=lambda x: x.published_date)
            witnesses.append({"route": route, "article_id": first_after.article_id, "date": str(first_after.published_date), "role": "after_end_frontier"})
        if min(dates) < start:
            witnesses.append({"route": route, "article_id": listed[-1].article_id, "date": str(min(dates)), "role": "before_start_frontier"})
            break
        page += 1
    # Category routes are corroborating official acquisition routes, not a
    # replacement for the live route. They also help recover route divergence.
    for typ in CATEGORY_TYPES:
        route = f"{LIVE_ROUTE}?{urlencode({'type': typ})}"
        status, body, _ = client.get(route)
        routes.append(route)
        if status == 200 and body:
            collected.extend(parse_listing(body, route))
        else:
            exceptions.append(f"CATEGORY_ROUTE_UNAVAILABLE:{route}:HTTP_{status}")
    # bounded ID continuity signal: report IDs in the scope and immediate
    # official boundary witnesses; never infer missing articles from gaps.
    in_scope = [x for x in collected if start <= x.published_date <= end]
    ids = sorted(int(x.article_id) for x in in_scope)
    if ids:
        expected = set(range(min(ids), max(ids) + 1))
        missing = sorted(expected - set(ids))
        if missing:
            exceptions.append("ID_GAP_RECORDED_NOT_INFERRED_AS_MISSING:" + ",".join(map(str, missing)))
    return DiscoveryResult(in_scope, routes, page, witnesses, exceptions)
