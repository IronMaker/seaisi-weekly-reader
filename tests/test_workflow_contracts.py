from datetime import date

from seaisi_weekly_reader.parser import canonical_url, parse_listing, parse_detail
from seaisi_weekly_reader.retrieval import completeness_gate, retrieve_official, RetrievalIncomplete


def test_canonical_url_drops_query_but_keeps_seaisi_detail():
    assert canonical_url("https://www.seaisi.org/details/28280?type=news-rooms") == "https://www.seaisi.org/details/28280?type=news-rooms"


def test_listing_parser_extracts_date_title_and_id():
    html = '<a href="https://www.seaisi.org/details/28280?type=news-rooms">Members daily output Steel Industry 17 August 2026</a>'
    result = parse_listing(html, "live")
    assert result[0].article_id == "28280"
    assert result[0].published_date == date(2026, 8, 17)
    assert result[0].title == "Members daily output"


def test_detail_parser_extracts_august_date_and_body():
    published, title, body = parse_detail('<p>Posted on 17 Aug 2026</p><h4>Title</h4><p>Body text.</p>')
    assert published == date(2026, 8, 17)
    assert title == "Title"
    assert body == "Body text."


def test_three_round_recovery_stays_official_and_readable():
    seen = []
    def fetch(url):
        seen.append(url)
        if len(seen) == 2:
            return 200, "official body", "https://www.seaisi.org/details/1"
        return 404, "", url
    class Item: detail_url = "https://www.seaisi.org/details/1"; title = "Title"
    record = retrieve_official(Item(), fetch, lambda _: "https://www.seaisi.org/news-rooms?search=Title")
    assert record.status == "READ_OK"
    assert len(record.attempts) == 2


def test_forced_one_unreadable_fails_closed():
    try:
        completeness_gate(["READ_OK", "FAILED"])
    except RetrievalIncomplete:
        return
    raise AssertionError("completeness gate must fail closed")
