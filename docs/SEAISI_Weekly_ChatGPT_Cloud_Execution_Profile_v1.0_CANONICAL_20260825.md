# SEAISI Weekly ChatGPT Cloud Execution Profile v1.0 — CANONICAL

Status: CANONICAL_EXECUTION_PROFILE
Effective date: 2026-08-25
Repository: IronMaker/seaisi-weekly-reader
Parent content contract: SEAISI Weekly Application Profile v2.1 — Canonical Inventory Recovery

## 1. Purpose

This profile fixes the execution boundary used when the user invokes `執行 SEAISI Weekly Reader Workflow` from ChatGPT.

The GitHub repository and its GitHub Actions cloud runtime are the canonical live execution path. ChatGPT is the orchestrator/reviewer and MUST NOT silently replace the canonical acquisition run with an independent web-search reconstruction.

## 2. Canonical execution chain

On invocation, use this authority order:

1. Compute/verify the previous complete weekly boundary: Wednesday 00:00 through Tuesday 23:59, Asia/Taipei.
2. Inspect the latest `SEAISI Weekly Cloud Autorun` run and its producer evidence for that exact boundary.
3. If a successful authoritative run for that boundary already exists, consume that run; do not reacquire merely to make the result look newer.
4. If no authoritative run exists for the required boundary, invoke/use the repository's canonical cloud execution path when the connected GitHub capability permits it. If direct dispatch is unavailable, do not fabricate execution; report the execution boundary explicitly.
5. Accept publication only when producer authority is `PASS`, inventory/body completeness passes, and the publication authority contract permits the output.
6. Read/report the resulting publication and delivery state.

## 3. Freshness contract

`latest` means the most recent COMPLETE Wed–Tue sampling window, not the current partial week.

A prior-week publication MUST NOT be presented as current when the required complete boundary has advanced.

The canonical producer performs live SEAISI acquisition at execution time. Cached ChatGPT prose, old reports, search snippets, or prior inventory counts are not freshness evidence.

## 4. Source/content authority

All source and body rules remain governed by Application Profile v2.1:
- SEAISI News Rooms / official SEAISI detail pages only for article content;
- frozen inventory before formal publication;
- at most three official-route body-retrieval attempts;
- no external article-body substitution;
- unresolved completeness => execution report, not formal weekly report.

## 5. Producer/publication authority

The producer is authoritative for acquisition status. The publisher MUST NOT upgrade producer `FAIL` to `FORMAL_REPORT_PUBLISHED` merely because all observed bodies are `READ_OK` or an older Markdown file exists.

Formal publication requires all of:
- exact required weekly boundary;
- `producer_status = PASS`;
- body completeness PASS;
- no unresolved inventory authority defect;
- approved formal report content for that same boundary.

Otherwise publication is withheld or marked editorial pending / failed execution as appropriate.

## 6. ChatGPT invocation behavior

When the user says `執行 SEAISI Weekly Reader Workflow`, ChatGPT should:

`resolve boundary -> inspect canonical GitHub run -> verify producer/completeness authority -> use/trigger canonical cloud execution as available -> read publication/evidence -> report status -> verify email delivery state`

ChatGPT MUST NOT default to an independent SEAISI web crawl when the canonical GitHub execution path is available.

If the latest required boundary has no completed canonical run, say so explicitly. Do not return an older report as though it were latest.

## 7. Delivery

The canonical output remains:
- formal Traditional-Chinese, de-identified Markdown/publication after all gates pass; or
- explicit failed execution report when gates do not pass.

Email target and subject contract remain governed by the user-authorized workflow configuration. Email failure or missing delivery configuration MUST be explicitly reported and MUST NOT be represented as successful delivery.

## 8. Runtime independence

GitHub-hosted execution is the canonical unattended runtime. The user's Mac does not need to be powered on for scheduled cloud acquisition/publication.

## 9. Compatibility

This profile changes execution routing and freshness authority only. It does not supersede Application Profile v2.1 source, inventory, retrieval, completeness, editorial, de-identification, or delivery requirements.
