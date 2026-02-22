# Gymnastics Vertical — Hugo Reset Handoff v3

Author: Matthew Sword  
Persona: Codex Fleetwood  
Status: HARD RESET  
Date: 2026-02-22

---

## Objective

Stabilize Hugo static site generation for Gymnastics Vertical through a deterministic reset of Firestore data, markdown export, and layout/content naming.

## Scope

- Delete and reseed canonical module collections.
- Enforce canonical section naming and plural-only folder policy.
- Remove duplicate/ambiguous content folders.
- Align layout folders to section names exactly.
- Enforce deterministic export and local Hugo build verification.

## Schema Impact

- Canonical section names are fixed:
  - `gymnasts`
  - `coaches`
  - `competitions`
  - `meets`
- Prohibited section/folder names:
  - `athlete`
  - `athletes`
  - `competition` (singular)
  - `coach` (singular folder)
- Front matter requirements:
  - `draft: false`
  - `status: active` for list visibility
  - Unique `federationId`
  - Slug derived from name

## Export Impact

- Export target is only `/content/<section>/`.
- Export must wipe canonical sections before writing:
  - `content/gymnasts`
  - `content/coaches`
  - `content/competitions`
  - `content/meets`
- Orphaned markdown files must be removed during regeneration.
- Mixed export roots and singular/plural parallel output are forbidden.

## Risks

- Naming drift between content and layout can break section rendering.
- Legacy markdown artifacts can produce duplicates and stale pages.
- Blind seed writes can create duplicate entities.
- Template fallback behavior can hide structural defects until deploy.

## Required Verification Steps

1. `hugo server` runs clean locally.
2. `/gymnasts` renders only active gymnasts.
3. Individual gymnast page renders correctly.
4. `/coaches` renders correctly.
5. `/competitions/2025` renders correctly.
6. No false empty-state messaging when data exists.
7. No duplicate content pages across canonical sections.

Only after all checks pass: proceed to Firebase deploy.

## Persona Handoff Prompts

### Backend Persona Prompt

Enforce canonical section naming (`gymnasts`, `coaches`, `competitions`, `meets`) across seed/export logic, apply upsert-by-`federationId`, and ensure `status=active` plus `draft=false` defaults on write. Remove singular/plural drift and validate no duplicate content output paths are generated.

### Template Persona Prompt

Audit Hugo layouts so each section maps to matching layout folder names and modern list filtering uses `.RegularPages` + `status=active`. Remove fallback ambiguity and verify section pages and singles render under canonical folders only.

### QA Persona Prompt

Run local `hugo server` checks for `/gymnasts`, `/coaches`, `/competitions/2025`, and individual gymnast pages. Confirm no stale markdown artifacts, no duplicate pages, and no false empty-state output.

### Deploy Persona Prompt

Block deploy unless local Hugo verification passes and export has completed full section wipes plus deterministic regeneration. Do not allow mixed export roots or residual legacy folders.

## Immediate Tasks

1. Delete ambiguous folders.
2. Standardize vocabulary and plural section naming.
3. Fix section `list.html` templates to modern Hugo pattern.
4. Fix section `single.html` templates to deterministic field rendering.
5. Remove old export artifacts.
6. Add dedupe logic to seeder.
7. Reseed clean.
8. Run local Hugo build.
9. Confirm stable output.
10. Re-enable export pipeline.

## Outcome Definition

Success means:

- Clean Hugo structure.
- Deterministic builds.
- No duplicate content.
- No naming ambiguity.
- Stable export process.
