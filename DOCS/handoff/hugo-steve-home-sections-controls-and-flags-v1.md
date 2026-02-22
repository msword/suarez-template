# Codex Hugo (Steve) Handoff — Home Sections UI Controls and Flags v1

Author: Matthew Sword  
Persona: Codex Fleetwood  
Target Persona: Codex Hugo (Steve)  
Status: Active  
Date: 2026-02-22

---

## Objective

Implement deterministic Home Sections rendering controls in Hugo using exported `data/home/sections.*` and `data/meta/site.*` payloads.

---

## Scope

This update covers template render behavior for:

- `columns` (`1` or `2`)
- `layout` (`image_left_content_right`, `content_left_image_right`, `image_left_image_right`, `content_left_content_right`)
- `left`/`right` side payload model
- section and side-level `items`
- section `active` and `order`

No runtime API calls were added.

---

## Data Source

Render source is Hugo `site.Data`:

- `site.Data.home.sections`
- fallback from `site.Data.meta.site.home.sections`
- export fallback from `sitecms-export/<org>/<timestamp>/data/home/sections.yaml`
- export fallback also supports `sections.yml`

---

## Render Rules Implemented

1. Sections are filtered to active.
2. Sections are sorted ascending by `order`.
3. `columns=1` renders single-column section content.
4. `columns=2` renders split layout with left/right side handling.
5. `layout` controls side type interpretation.
6. Side-level payloads (`left`, `right`) are used when present.
7. Backward compatibility preserved for legacy `mediaUrl` sections.

---

## Template Changes

- `layouts/partials/home_sections.html`
  - Added full control-flag aware rendering for `columns/layout/left/right/items`.
- `layouts/partials/data_bundle.html`
  - Ensured home sections fallback loading is independent and supports `.yaml` and `.yml`.

---

## Risks

1. Invalid `columns/layout` payload values degrade to safe defaults.
2. Missing side payload fields can produce intentionally sparse sections.
3. Mixed old/new payloads may render with fallback behavior by design.

---

## Required Verification Steps

1. Build site with `hugo --minify`.
2. Confirm home sections render under hero from `data/home/sections.yaml`.
3. Confirm 2-column section renders media/content according to `layout`.
4. Confirm inactive sections are not rendered.
5. Confirm ordering respects `order`.

