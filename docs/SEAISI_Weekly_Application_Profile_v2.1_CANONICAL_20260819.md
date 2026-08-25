# SEAISI Weekly Application Profile v2.1 — Canonical Inventory Recovery

Status: CANONICAL_PROFILE_PATCH
Effective date: 2026-08-19
Parent asset: Steel Insights v6 Standalone Extraction & Static Site Delivery
Supersedes: SEAISI Weekly Application Profile v2.0 inventory-discovery behavior only

## 1. Weekly boundary

Each run processes only the previous complete weekly window:
- Start: previous Wednesday 00:00
- End: current Tuesday 23:59
- Timezone: Asia/Taipei

## 2. Source authority

The only content authority is SEAISI News Rooms and official SEAISI detail pages.
External sites, search snippets, and third-party mirrors may not supply article body content.
Search-engine/index results are non-authoritative discovery aids only.

## 3. Stage 1 — Canonical inventory discovery

Inventory acquisition MUST use official-source routes in this order:

1. Live News Rooms routes.
2. Official category News Rooms routes.
3. Official equivalent URL variants where available.
4. Detail-ID continuity/frontier recovery from the last verified SEAISI News Rooms detail ID.

The canonical weekly inventory is the union of successful official-source discoveries, deduplicated by canonical detail URL / detail ID, then filtered by the weekly date boundary.

### 3.1 Detail-ID continuity/frontier rule

When live/category inventory may be stale or incomplete:
- start from a verified neighboring detail ID;
- test bounded adjacent IDs mechanically;
- accept only pages that resolve as SEAISI News Rooms detail pages;
- parse publication date, title, canonical URL, and body availability;
- include only records whose publication date falls inside the weekly boundary;
- use adjacent records outside the weekly boundary as boundary evidence;
- do not infer a missing article from an unobserved ID alone.

### 3.2 Inventory authority rule

`SEARCH_INDEX_STALE` is not `SOURCE_UNAVAILABLE`.

A stale `/index.php/news-rooms`, search-engine cache, or crawler representation MUST NOT by itself trigger `BLOCKED_AT_SOURCE_INVENTORY`.

`BLOCKED_AT_SOURCE_INVENTORY` is permitted only after the official live/category/equivalent routes plus bounded detail-ID continuity recovery fail to establish a defensible inventory boundary.

## 4. Stage 2 — Article body retrieval

For every frozen inventory item:
1. Open the official detail URL directly.
2. If blank, stale, or cache-missed, recover through official SEAISI routes using the exact title/detail identity.
3. Retry through at most three official paths.
4. Never substitute title-only data, search snippets, or external article text for the official body.

## 5. Completeness gate

Formal weekly publication is allowed only when:
- inventory boundary is defensible from official routes and/or detail-ID continuity;
- every frozen inventory item has an official detail URL;
- every item body has been successfully read;
- no unresolved inventory item remains.

If any item remains unresolved, output an execution report instead of a formal weekly report.

## 6. Error taxonomy

Use explicit failure classes:
- `SEARCH_INDEX_STALE`
- `URL_ROUTE_DIVERGENCE`
- `DETAIL_RETRIEVAL_FAILED`
- `INVENTORY_BOUNDARY_UNPROVEN`
- `HTTP_403`
- `HTTP_429`
- `CAPTCHA_OR_EXPLICIT_BLOCK`
- `SOURCE_UNAVAILABLE`

Do not describe SEAISI as blocking machine access unless direct evidence shows HTTP 403, HTTP 429, CAPTCHA, or an explicit blocking message.

## 7. Output and delivery

After the completeness gate passes:
1. perform Traditional Chinese editorial processing;
2. perform external-publication de-identification;
3. output Markdown;
4. email the formal report to the configured recipient with subject containing `SEAISI 週報` and the sampling date range.

If email sending fails, report the exact delivery failure explicitly.

## 8. Regression evidence establishing v2.1

Two complete historical recovery runs passed using the new discovery method:

- 2026-08-05 through 2026-08-11: 20 articles; 20/20 official bodies readable.
- 2026-08-12 through 2026-08-18: 14 articles; 14/14 official bodies readable.

Observed root cause of the earlier false block:
`STALE/INCONSISTENT RETRIEVAL ROUTE` rather than SEAISI source unavailability.

Validated recovery pattern:
`LIVE/CATEGORY DISCOVERY -> UNION/DEDUPE -> DATE FILTER -> DETAIL-ID CONTINUITY CHECK -> FROZEN INVENTORY -> BODY COMPLETENESS GATE`

## 9. Compatibility boundary

This patch changes Stage 1 inventory discovery and related error classification only.
It does not change:
- weekly date boundaries;
- SEAISI-only content authority;
- body completeness requirement;
- editorial/de-identification sequence;
- three-path official retry principle;
- failure-report behavior;
- email-delivery requirement.

