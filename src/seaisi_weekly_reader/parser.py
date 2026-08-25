from __future__ import annotations

import html
import re
from dataclasses import dataclass
from datetime import date
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit, urlunsplit

BASE = "https://www.seaisi.org"
DATE_RE = re.compile(r"Posted on\s+(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})", re.I)
DETAIL_RE = re.compile(r"/details/(\d+)")


def canonical_url(url: str) -> str:
    p = urlsplit(urljoin(BASE, url))
    # SEAISI currently requires type=news-rooms for detail retrieval. Keep
    # that official route selector while normalizing host/scheme.
    query = "type=news-rooms" if p.query and "type=news-rooms" in p.query else p.query
    return urlunsplit(("https", "www.seaisi.org", p.path, query, ""))


@dataclass(frozen=True)
class ListedArticle:
    published_date: date
    title: str
    detail_url: str
    article_id: str
    category: str = ""
    source_route: str = ""


class ListingParser(HTMLParser):
    def __init__(self, source_route: str = ""):
        super().__init__(convert_charrefs=True)
        self.source_route = source_route
        self.current_href = ""
        self.current_text: list[str] = []
        self.links: list[tuple[str, str]] = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            href = dict(attrs).get("href", "")
            if DETAIL_RE.search(href):
                self.current_href, self.current_text = href, []

    def handle_data(self, data):
        if self.current_href:
            self.current_text.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self.current_href:
            self.links.append((self.current_href, " ".join("".join(self.current_text).split())))
            self.current_href, self.current_text = "", []


def parse_listing(body: str, source_route: str = "") -> list[ListedArticle]:
    parser = ListingParser(source_route)
    parser.feed(body)
    result: list[ListedArticle] = []
    for href, text in parser.links:
        match = DETAIL_RE.search(href)
        if not match:
            continue
        # Listing anchors contain title, category, and date. The date is the
        # final DD Month YYYY triplet; preserve the title before the category.
        dm = re.search(r"(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})\s*$", text)
        if not dm:
            continue
        try:
            from datetime import datetime
            published = datetime.strptime(" ".join(dm.groups()), "%d %B %Y").date()
        except ValueError:
            continue
        prefix = text[: dm.start()].strip()
        category = ""
        categories = ("SEAISI Articles", "Steel Industry", "Business/Economics", "Steel Prices", "Trade Measure")
        title, category = prefix, ""
        for candidate in categories:
            if prefix.endswith(candidate):
                title, category = prefix[:-len(candidate)].strip(), candidate
                break
        result.append(ListedArticle(published, html.unescape(title).strip(), canonical_url(href), match.group(1), category, source_route))
    return result


class DetailParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.h1: list[str] = []
        self.h4: list[str] = []
        self.posted: list[str] = []
        self.paragraphs: list[str] = []
        self._tag = ""
        self._buf: list[str] = []
        self._seen_heading = False

    def handle_starttag(self, tag, attrs):
        if tag in ("h1", "h4", "p"):
            self._tag, self._buf = tag, []

    def handle_data(self, data):
        if self._tag:
            self._buf.append(data)

    def handle_endtag(self, tag):
        if tag != self._tag:
            return
        text = " ".join("".join(self._buf).split())
        if text:
            if tag == "h1": self.h1.append(text)
            elif tag == "h4": self.h4.append(text)
            elif tag == "p":
                if DATE_RE.search(text): self.posted.append(text)
                self.paragraphs.append(text)
        self._tag, self._buf = "", []


def parse_detail(body: str) -> tuple[date | None, str, str]:
    parser = DetailParser()
    parser.feed(body)
    published = None
    if parser.posted:
        m = DATE_RE.search(parser.posted[0])
        if m:
            from datetime import datetime
            try: published = datetime.strptime(" ".join(m.groups()), "%d %b %Y").date()
            except ValueError: pass
    title = parser.h4[0] if parser.h4 else (parser.h1[-1] if parser.h1 else "")
    body_parts = [p for p in parser.paragraphs if not DATE_RE.search(p) and p != "Source:Mysteel Global" and not p.startswith("Source:")]
    body_text = "\n\n".join(body_parts)
    return published, title, body_text
