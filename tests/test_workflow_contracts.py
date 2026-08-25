from datetime import date

from seaisi_weekly_reader.parser import canonical_url, parse_listing, parse_detail
from seaisi_weekly_reader.retrieval import completeness_gate, retrieve_official, RetrievalIncomplete
from seaisi_weekly_reader.gold import reconcile_gold
from seaisi_weekly_reader.inventory import InventoryItem
from seaisi_weekly_reader.cloud_publish import publish
import json
from pathlib import Path


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


def _items(count=15, status="READ_OK", domain="www.seaisi.org", in_scope=True):
    d = date(2026, 8, 18) if in_scope else date(2026, 8, 19)
    return [InventoryItem(d, f"Article {i}", f"https://{domain}/details/{28000+i}?type=news-rooms", status, str(28000+i)) for i in range(count)]


def test_gold_correction_accepts_valid_official_extra_and_fixture_28285():
    fixture = json.loads(Path(__file__).parent.joinpath("fixtures/known_week_gold_v1.json").read_text())
    items = _items(14) + [InventoryItem(date(2026, 8, 18), fixture["official_added_article"]["title"], fixture["official_added_article"]["detail_url"], "READ_OK", "28285")]
    result = reconcile_gold(14, items, date(2026, 8, 12), date(2026, 8, 18))
    assert result.status == "PASS_WITH_GOLD_CORRECTION"
    assert result.accepted_count == 15


def test_invalid_extra_article_is_not_silently_accepted():
    result = reconcile_gold(14, _items(14) + _items(1, domain="example.com"), date(2026, 8, 12), date(2026, 8, 18))
    assert result.status == "GOLD_DIVERGENCE_UNRESOLVED"


def test_missing_live_article_is_unresolved():
    result = reconcile_gold(15, _items(14), date(2026, 8, 12), date(2026, 8, 18))
    assert result.status == "GOLD_DIVERGENCE_UNRESOLVED"


def _publication_fixture(tmp_path: Path, producer_status: str):
    artifact = tmp_path / "artifact"
    artifact.mkdir()
    manifest = {
        "boundary": {"start": "2026-08-12T00:00:00+08:00", "end": "2026-08-18T23:59:59+08:00"},
        "producer_status": producer_status,
        "producer_reason": "test authority",
    }
    inventory = [{"published_date": "2026-08-12", "title": "A", "detail_url": "https://www.seaisi.org/details/1?type=news-rooms", "read_status": "READ_OK"}]
    (artifact / "run_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    (artifact / "inventory.json").write_text(json.dumps(inventory), encoding="utf-8")
    (tmp_path / "reports").mkdir()
    (tmp_path / "docs").mkdir()
    (tmp_path / "reports" / "SEAISI_Weekly_2026-08-12_2026-08-18.md").write_text("# Approved formal report", encoding="utf-8")
    return artifact


def test_publication_cannot_override_failed_producer_even_when_all_bodies_read_and_formal_md_exists(tmp_path):
    artifact = _publication_fixture(tmp_path, "FAIL")
    result = publish(artifact, tmp_path)
    assert result["status"] == "FAILED_EXECUTION_REPORT"
    assert "Approved formal report" not in (tmp_path / "docs" / "latest.html").read_text(encoding="utf-8")


def test_publication_allows_formal_report_only_with_producer_pass(tmp_path):
    artifact = _publication_fixture(tmp_path, "PASS")
    result = publish(artifact, tmp_path)
    assert result["status"] == "FORMAL_REPORT_PUBLISHED"
    assert "Approved formal report" in (tmp_path / "docs" / "latest.html").read_text(encoding="utf-8")
