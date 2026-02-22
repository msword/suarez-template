# Codex Hugo (Steve) Handoff — Data Files and Rules Update

Author: Matthew Sword  
Persona: Codex Fleetwood  
Target Persona: Codex Hugo (Steve)  
Status: Active  
Date: 2026-02-22

---

## Objective

Document the new Gymnastics export data contract so Hugo templates can reliably render org metadata, navigation, and calendar events from `data/`.

This handoff is specifically for template/build behavior alignment.

---

## What Changed

Two export paths now write richer site data:

1. SiteCMS export path (`app/services/hugo_service.py`)  
2. Gymnastics module publish path (`modules/gymnastics/service.py`)

Both paths now export calendar events and metadata bundles in addition to org and navigation.

---

## Where Data Lives (Render Source)

Steve should render from Hugo `site.Data` loaded out of the export workspace `data/` folder.

### SiteCMS local export/build path

1. API export writes a timestamped workspace:
   - `generated/sitecms-export/<orgId>/<timestamp>/`
2. Data files used by Hugo are here:
   - `generated/sitecms-export/<orgId>/<timestamp>/data/`
3. Local static build output is here:
   - `generated/sitecms-local/<orgId>/public/`

At render/build time, template reads resolve from the export workspace:

- `site.Data.org` -> `data/org.yaml`
- `site.Data.navigation` -> `data/navigation.yaml`
- `site.Data.site.settings` -> `data/site/settings.yaml`
- `site.Data.calendar.events` -> `data/calendar/events.yaml`
- `site.Data.meta.site` -> `data/meta/site.yaml`

### Module publish path

When module publish writes directly to `generated/`, data files are here:

- `generated/data/org.json`
- `generated/data/navigation.json`
- `generated/data/site/settings.json`
- `generated/data/calendar/events.json`
- `generated/data/meta/site.json`

At render/build time for this path:

- `site.Data.org` -> `data/org.json`
- `site.Data.navigation` -> `data/navigation.json`
- `site.Data.site.settings` -> `data/site/settings.json`
- `site.Data.calendar.events` -> `data/calendar/events.json`
- `site.Data.meta.site` -> `data/meta/site.json`

---

## New and Required Data Files

### SiteCMS export (YAML)

- `data/org.yaml`
- `data/navigation.yaml`
- `data/site/settings.yaml`
- `data/calendar/events.yaml`
- `data/home/sections.yaml`
- `data/meta/site.yaml`
- `data/hero.yaml` (existing, still generated)

### Module publish export (JSON)

- `data/org.json`
- `data/navigation.json`
- `data/site/settings.json`
- `data/calendar/events.json`
- `data/meta/site.json`
- `data/scores/<meetId>.json` (existing behavior)

---

## Data Contract Summary

### `org`

Must include:

- `orgId`
- `orgName`
- `contact.email`
- `contact.phone`
- `contact.website`
- `profile.address.line1`
- `profile.address.line2`
- `profile.address.city`
- `profile.address.state`
- `profile.address.postalCode`
- `profile.address.country`

Address fields are exported as empty strings when missing (keys should not disappear).

### `navigation`

Must include:

- `items` array

Item shape:

- `label` (required)
- `url` (optional)
- `order` (optional)
- `children` (optional recursive array)

### `site/settings`

Site settings payload for template meta/theme/title/navigation behavior.

Templates currently use this directly via:

- `site.Data.site.settings`

### `calendar/events`

Must include:

- `events` array

Each event should include:

- `id`
- `title`
- `description`
- `location`
- `start_at`
- `end_at`
- `all_day`
- `timezone`
- `status`
- `updated_at`

Source of truth:

- `orgs/{orgId}/events`

Sort order:

1. `start_at`
2. `title`
3. `id`

### `home/sections`

Must include:

- `sections` array

Each section supports:

- `id`
- `order`
- `component`
- `title`
- `subtitle`
- `bodyMarkdown`
- `ctaLabel`
- `ctaUrl`
- `mediaUrl`
- `items` (array)
- `config` (object)
- `active`

### `meta/site`

Aggregate payload for future growth:

- `org`
- `navigation`
- `settings`
- `calendar`
- `generatedAt`

Use this as the forward-compatible extension point for new global/site-level configs.

---

## Rules Added

Canonical rule file:

- `docs/modules/gymnastics/rules/vertical-data-export-contract.md`

Registered in documentation governance:

- `docs/modules/gymnastics/rules/documentation-rules.md`

Non-negotiable rules now include:

1. Exporters must always emit org + navigation + calendar data.
2. Calendar export is mandatory for Gymnastics.
3. Runtime pages must not read Firestore directly.
4. New site-level config must be added to `data/meta/site.*` and documented.

---

## Template Notes for Steve

Current template dependencies already in place:

- `partials/head.html` reads `site.Data.site.settings`
- `partials/header.html` reads `site.Data.site.settings` + `site.Data.navigation`
- `partials/footer.html` reads `site.Data.org`

Calendar data is now available for rendering through:

- `site.Data.calendar.events`

Home sections are now available for rendering through:

- `site.Data.home.sections`

Navigation UI rules implemented in templates:

1. Top navigation labels are rendered in Title Case.
2. Maximum visible page links in top nav is 5 (theme icon is separate).
3. If links exceed 5:
   - First 4 links render directly.
   - The 5th becomes a dropdown trigger.
   - Dropdown shows up to 5 links.
   - If overflow exceeds 5, a final `More` link points to `/pages`.

No runtime API calls are required to build a calendar page.

## War Room UI Update: Brand Colors + Footer

New template behavior consumes theme colors from `meta/site` and applies them globally:

1. Header navigation links:
   - light mode uses `primaryColor`
   - dark mode uses `accentColor` for contrast safety
2. Footer:
   - background uses `primaryColor`
   - text and icon color uses `accentColor`
   - min-height is `300px`
3. Footer social links:
   - render only when social URL exists in exported org social maps
   - use inline icon set aligned with current moon/sun SVG style
4. Brand color source priority:
   1. `settings.theme.primaryColor` / `settings.theme.accentColor`
   2. fallback `org.branding.primaryColor` / `org.branding.accentColor`

This is the new baseline format to consume for Suarez branding behavior.

---

## Implementation References

- `app/services/hugo_service.py`
- `modules/gymnastics/service.py`
- `docs/modules/gymnastics/rules/vertical-data-export-contract.md`
- `docs/modules/gymnastics/rules/documentation-rules.md`

---

## Required Verification

Before publish/deploy:

1. Confirm export contains required `data/` files for chosen pipeline.
2. Confirm `org` includes address keys.
3. Confirm `navigation.items` exists.
4. Confirm `calendar.events` exists (can be empty array, but key must exist).
5. Confirm template build succeeds using only exported files.

---

## Implementation Status In This Repo

Implemented in templates:

- `layouts/partials/head.html`
- `layouts/partials/header.html`
- `layouts/partials/footer.html`
- `layouts/calendar/list.html`
- `layouts/calendar/single.html`
- `layouts/partials/home_sections.html`

Runtime behavior:

- Renders from `site.Data.*` only (no runtime Firestore reads)
- Supports both contract-safe object form (`calendar.events.events`) and slice form (`calendar.events`) for compatibility
- Supports `home/sections` rendering from `site.Data.home.sections` with export fallback loading
- Derives Events route org segment from exported `org.orgId` when present
