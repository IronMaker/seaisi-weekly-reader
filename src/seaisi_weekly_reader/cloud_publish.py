from __future__ import annotations

import argparse
import html
import json
import shutil
from pathlib import Path

import markdown


def _shell(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang=\"zh-Hant\">
<head>
<meta charset=\"utf-8\">
<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">
<title>{html.escape(title)}</title>
<style>
body{{max-width:900px;margin:40px auto;padding:0 24px;font-family:-apple-system,BlinkMacSystemFont,'PingFang TC','Noto Sans TC',sans-serif;line-height:1.75;color:#1f2328}}
h1,h2,h3{{line-height:1.35}} a{{color:#0969da}} table{{border-collapse:collapse;width:100%;display:block;overflow:auto}} th,td{{border:1px solid #d0d7de;padding:8px;vertical-align:top}} code{{background:#f6f8fa;padding:2px 4px;border-radius:4px}} .meta{{color:#57606a}} .status{{font-weight:700}}
</style>
</head><body>{body}</body></html>"""


def publish(artifact_dir: Path, repo_root: Path) -> dict:
    manifest = json.loads((artifact_dir / "run_manifest.json").read_text(encoding="utf-8"))
    inventory = json.loads((artifact_dir / "inventory.json").read_text(encoding="utf-8"))
    start = manifest["boundary"]["start"][:10]
    end = manifest["boundary"]["end"][:10]
    read_ok = sum(1 for x in inventory if x.get("read_status") == "READ_OK")
    complete = bool(inventory) and read_ok == len(inventory)

    reports_dir = repo_root / "reports"
    canonical_md = reports_dir / f"SEAISI_Weekly_{start}_{end}.md"
    docs_runs = repo_root / "docs" / "runs"
    docs_runs.mkdir(parents=True, exist_ok=True)
    target = docs_runs / f"{start}_{end}.html"

    if complete and canonical_md.exists():
        md_text = canonical_md.read_text(encoding="utf-8")
        body = markdown.markdown(md_text, extensions=["tables", "fenced_code"])
        status = "FORMAL_REPORT_PUBLISHED"
        title = f"SEAISI 週報｜{start}–{end}"
    else:
        rows = "\n".join(
            f"<tr><td>{html.escape(str(x.get('published_date','')))}</td><td>{html.escape(x.get('title',''))}</td><td><a href=\"{html.escape(x.get('detail_url',''))}\">official</a></td><td>{html.escape(x.get('read_status',''))}</td></tr>"
            for x in inventory
        )
        if complete:
            status = "ACQUISITION_COMPLETE_EDITORIAL_PENDING"
            note = "官方正文已全部取得，但此週期尚無經核准的繁中正式稿；因此不冒充正式週報。"
        else:
            status = "FAILED_EXECUTION_REPORT"
            note = "正文完整性未通過；正式週報依規則 withheld。"
        title = f"SEAISI Weekly Reader｜{start}–{end}"
        body = f"""
<h1>{html.escape(title)}</h1>
<p class=\"status\">{status}</p>
<p>{html.escape(note)}</p>
<p class=\"meta\">Inventory: {len(inventory)} ｜ READ_OK: {read_ok}/{len(inventory)} ｜ External substitution: 0</p>
<table><thead><tr><th>Date</th><th>Title</th><th>Source</th><th>Status</th></tr></thead><tbody>{rows}</tbody></table>
"""

    target.write_text(_shell(title, body), encoding="utf-8")
    shutil.copyfile(target, repo_root / "docs" / "latest.html")

    index = f"""<!doctype html>
<html lang=\"zh-Hant\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><title>SEAISI Weekly Reader</title></head>
<body style=\"max-width:900px;margin:40px auto;padding:0 24px;font-family:-apple-system,BlinkMacSystemFont,'PingFang TC','Noto Sans TC',sans-serif;line-height:1.7\">
<h1>SEAISI Weekly Reader</h1>
<p>Latest cloud publication status: <strong>{status}</strong></p>
<ul><li><a href=\"runs/{start}_{end}.html\">{start} ～ {end}</a></li></ul>
</body></html>"""
    (repo_root / "docs" / "index.html").write_text(index, encoding="utf-8")
    result = {"start": start, "end": end, "status": status, "inventory": len(inventory), "read_ok": read_ok, "published": str(target)}
    print(json.dumps(result, ensure_ascii=False))
    return result


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("artifact_dir", type=Path)
    p.add_argument("--repo-root", type=Path, default=Path("."))
    args = p.parse_args()
    publish(args.artifact_dir, args.repo_root)


if __name__ == "__main__":
    main()
