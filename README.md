# SEAISI Weekly Reader

SEAISI Weekly Reader is a deterministic weekly steel-news retrieval and publication workflow for SEAISI News Rooms.

## Current Canonical Profile

- Version: v2.1
- Canonical document:
  `docs/SEAISI_Weekly_Application_Profile_v2.1_CANONICAL_20260819.md`

## Weekly Boundary

Each run processes the previous completed weekly period:

Wednesday 00:00 → Tuesday 23:59  
Timezone: Asia/Taipei

## Core Workflow

1. Build and freeze the SEAISI News Rooms inventory.
2. Recover inventory using live/category routes and detail-ID continuity when needed.
3. Retrieve every official article body.
4. Apply the completeness gate.
5. Produce Traditional Chinese edited output only when all article bodies are available.
6. Produce a failure execution report instead of a formal weekly report when completeness fails.
7. Deliver the final report by email.

## Source Authority

Only SEAISI News Rooms is authoritative for report content.

External websites and search snippets must not be used to reconstruct article bodies.

## Repository Status

Current stage: canonical workflow documentation and reproducible implementation setup.
