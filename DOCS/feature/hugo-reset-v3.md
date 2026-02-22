# Gymnastics Vertical — Hugo Reset Feature v3

Author: Matthew Sword  
Persona: Codex Fleetwood  
Status: HARD RESET  
Date: 2026-02-22

---

## Purpose

Stabilize Gymnastics Vertical static generation by enforcing deterministic Hugo structure, canonical section naming, idempotent reseeding, and clean export boundaries.

## Problem It Solves

The current pipeline risk includes singular/plural naming drift, duplicate content roots, layout ambiguity, and stale markdown artifacts that produce non-deterministic Hugo outputs.

This reset removes ambiguity by enforcing a single vocabulary and strict section-to-layout alignment.

## Data Impact

- Firestore reset scope:
  - `gymnasts`
  - `coaches`
  - `competitions`
  - `meets`
- Seeder must enforce:
  - Unique `federationId`
  - Unique slug per org
  - `status` defaulting to `active`
  - `draft` defaulting to `false`
  - Upsert behavior by `federationId` instead of blind create

## Hugo Impact

- Canonical content sections are fixed to:
  - `gymnasts`
  - `coaches`
  - `competitions`
  - `meets`
- Layout folder names must exactly match section names.
- Section lists must use modern Hugo page access:
  - `where .RegularPages "Params.status" "active"`
- Legacy list access patterns are prohibited:
  - `.Pages`
  - `.Data.Pages`
  - `.Site.Pages`

## Firestore Impact

- Module reset deletes and re-seeds the four canonical collections only.
- Seed process must be idempotent and dedupe-safe.
- Duplicate federation identifiers are blocked at seed time.

## Export Impact

- Export writes only to `/content/<section>/`.
- Export must delete full section directories before regeneration:
  - `content/gymnasts`
  - `content/coaches`
  - `content/competitions`
  - `content/meets`
- Export must remove orphaned files and prevent mixed old/new folder trees.
- Export must never produce parallel singular/plural folder variants.

## Risk Analysis

- Risk: Legacy content folders survive and shadow new output.
  - Mitigation: Full section wipe before export regeneration.
- Risk: Section naming drift causes Hugo template fallback behavior.
  - Mitigation: Canonical naming + strict folder equality checks.
- Risk: Duplicate Firestore seed records create duplicate markdown pages.
  - Mitigation: Upsert by `federationId` and slug dedupe per org.
- Risk: Inactive records leak to public pages.
  - Mitigation: List templates filter `Params.status == "active"`.

## Rollback Strategy

- Restore last known-good markdown snapshot for `content/gymnasts`, `content/coaches`, `content/competitions`, and `content/meets`.
- Restore previous stable layouts under matching section folders.
- Revert seeder/export changes in a single rollback commit.
- Re-run Hugo local build verification before re-enabling publish.

## Implementation Summary

1. Delete ambiguous content/layout folders.
2. Enforce canonical section vocabulary in exporter and templates.
3. Replace list/single templates with deterministic modern Hugo patterns.
4. Add strict dedupe and defaults in seeder.
5. Verify local Hugo build and page-level rendering checks.
