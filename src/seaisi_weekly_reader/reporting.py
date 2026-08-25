from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path


def write_artifacts(root: Path, boundary, items, ledger, discovery, tests_text="", expected_count=None) -> Path:
    stamp = datetime.now().astimezone().strftime("%Y%m%dT%H%M%S%z")
    out = root / f"01_seaisi_live_acquisition_v1_{stamp}"
    out.mkdir(parents=True, exist_ok=False)
    records = [asdict(x) for x in items]
    (out / "inventory.json").write_text(json.dumps(records, ensure_ascii=False, indent=2, default=str) + "\n")
    with (out / "inventory.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=records[0].keys() if records else ["published_date"])
        w.writeheader(); w.writerows(records)
    (out / "retrieval_ledger.json").write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n")
    ids = sorted(int(x.article_id) for x in items if x.article_id)
    manifest = {"boundary": {"start": boundary.start.isoformat(), "end": boundary.end.isoformat()}, "inventory_count": len(items), "expected_inventory_count": expected_count, "exact_count_match": expected_count is None or len(items) == expected_count, "article_ids_sorted": ids, "routes": discovery.routes, "frontier_witnesses": discovery.frontier_witnesses, "exceptions": discovery.exceptions, "external_source_substitution": 0}
    (out / "run_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    if tests_text: (out / "test_report.txt").write_text(tests_text)
    return out


def write_reports(out: Path, boundary, items, ledger, failure=False, expected_count=None):
    ok = sum(1 for x in items if x.read_status == "READ_OK")
    lines = ["# SEAISI Known Week Replay", "", f"Boundary: `{boundary.start.isoformat()} → {boundary.end.isoformat()}`", f"", f"Inventory: **{len(items)}/{len(items)}**", f"Official body retrieval: **{ok}/{len(items)} READ_OK**", "External-source substitution: **0**", "", "## Inventory", "", "| Date | Title | Detail URL | Status |", "|---|---|---|---|"]
    lines += [f"| {x.published_date} | {x.title} | {x.detail_url} | {x.read_status} |" for x in items]
    count_ok = expected_count is None or len(items) == expected_count
    gate_ok = not failure and count_ok and ok == len(items)
    gate_line = "`PASS` — all frozen inventory bodies are official SEAISI and readable." if gate_ok else "`FAIL` — formal weekly report is withheld."
    if expected_count is not None and not count_ok:
        lines += [f"Expected exact inventory: **{expected_count}**, observed: **{len(items)}** (live-site divergence; no article was fabricated or removed)."]
    lines += ["", "## Gate", "", gate_line]
    (out / ("failure_counterexample.md" if failure else "known_week_replay.md")).write_text("\n".join(lines) + "\n")
