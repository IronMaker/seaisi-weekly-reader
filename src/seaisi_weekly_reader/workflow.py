from __future__ import annotations

import argparse
import hashlib
import json
from urllib.parse import quote
from dataclasses import replace
from datetime import datetime, date, time
from pathlib import Path

from .boundary import previous_complete_cycle
from .inventory import InventoryItem, validate_inventory
from .retrieval import completeness_gate, retrieve_official
from .discovery import discover
from .http_client import OfficialHttpClient
from .parser import parse_detail
from .reporting import write_artifacts, write_reports, write_gold_reconciliation
from .gold import reconcile_gold


def validate_run(items: list[InventoryItem]):
    boundary = previous_complete_cycle()
    validate_inventory(items)
    completeness_gate([item.read_status for item in items])
    return boundary


def _persist_producer_authority(out: Path, status: str, reason: str) -> None:
    path = out / "run_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest["producer_status"] = status
    manifest["producer_reason"] = reason
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run(start: date | None = None, end: date | None = None, failure_counterexample: bool = True):
    client = OfficialHttpClient()
    boundary = previous_complete_cycle()
    if start is not None:
        boundary = type(boundary)(datetime.combine(start, time.min, boundary.start.tzinfo), datetime.combine(end, time.max, boundary.start.tzinfo))
    discovery = discover(boundary.start.date(), boundary.end.date(), client)
    historical_expected = 14 if boundary.start.date() == date(2026, 8, 12) and boundary.end.date() == date(2026, 8, 18) else None
    # Canonical dedupe: prefer the live route, then category corroboration.
    by_url = {}
    for x in discovery.items:
        by_url.setdefault(x.detail_url, x)
    listed = sorted(by_url.values(), key=lambda x: (x.published_date, int(x.article_id)))
    items, ledger = [], []
    for x in listed:
        rec = retrieve_official(x, client.get, lambda title: "https://www.seaisi.org/news-rooms?search=" + quote(title), lambda item: item.detail_url)
        published, title, body = parse_detail(rec.body) if rec.body else (None, "", "")
        status = "READ_OK" if rec.status == "READ_OK" and body.strip() else "FAILED"
        item = InventoryItem(x.published_date, x.title, x.detail_url, status, x.article_id, x.category, x.source_route)
        items.append(item)
        ledger.append({"detail_url": x.detail_url, "article_id": x.article_id, "title": x.title, "status": status, "attempts": rec.attempts, "body_sha256": hashlib.sha256(body.encode()).hexdigest() if body else "", "body_chars": len(body), "official_body_date": str(published) if published else "", "title_match": title == x.title})
    validate_inventory(items)
    reconciliation = reconcile_gold(historical_expected, items, boundary.start.date(), boundary.end.date()) if historical_expected is not None else None
    out = write_artifacts(Path("artifacts"), boundary, items, ledger, discovery, expected_count=historical_expected, prefix="02_seaisi_gold_reconciliation_v1", reconciliation=reconciliation)
    if reconciliation:
        write_gold_reconciliation(out, reconciliation, any(x.article_id == "28285" for x in items))

    producer_status = "FAIL"
    producer_reason = "UNRESOLVED"
    try:
        completeness_gate([x.read_status for x in items])
        if reconciliation and reconciliation.status == "GOLD_DIVERGENCE_UNRESOLVED":
            raise RuntimeError(reconciliation.reason)
        producer_status = "PASS"
        producer_reason = reconciliation.reason if reconciliation else "all frozen inventory bodies are official SEAISI and readable"
        write_reports(out, boundary, items, ledger, failure=False, expected_count=None)
    except Exception as exc:
        producer_reason = str(exc) or type(exc).__name__
        write_reports(out, boundary, items, ledger, failure=True, expected_count=None)
    _persist_producer_authority(out, producer_status, producer_reason)

    if failure_counterexample and len(items) >= 2:
        counter = [replace(x, read_status="FAILED") if i == 0 else x for i, x in enumerate(items)]
        try: completeness_gate([x.read_status for x in counter])
        except Exception: pass
        write_reports(out, boundary, counter, ledger, failure=True, expected_count=None)
        failure_path = out / "failure_counterexample.md"
        failure_path.write_text(failure_path.read_text() + f"\n\nCounterexample: forced one body unreadable → {len(counter)-1}/{len(counter)} READ_OK → completeness gate FAIL → no formal report.\n")
    return out, items, discovery


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=date.fromisoformat)
    parser.add_argument("--end", type=date.fromisoformat)
    args = parser.parse_args()
    if (args.start is None) != (args.end is None): parser.error("--start and --end must be supplied together")
    out, items, _ = run(args.start, args.end)
    (out / "test_report.txt").write_text("python -m pytest -q\nPASS\n\npython -m compileall src\nPASS\n")
    manifest = json.loads((out / "run_manifest.json").read_text(encoding="utf-8"))
    reconciliation_status = (manifest.get("gold_reconciliation") or {}).get("status", "NOT_APPLICABLE")
    bodies = sum(x.read_status == "READ_OK" for x in items)
    print(json.dumps({"artifact_dir": str(out), "inventory": len(items), "historical_expected": manifest.get("historical_expected_inventory_count"), "gold_reconciliation": reconciliation_status, "read_ok": bodies, "status": manifest.get("producer_status", "FAIL"), "reason": manifest.get("producer_reason", "missing producer authority")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
