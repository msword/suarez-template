# Handoff: Fleetwood Export Snapshot Layout (Builder Input Contract)

Date: 2026-02-25  
Audience: Fleetwood Exporter Owner  
Owner: Fleetwood (export), Builder Owner (compile/deploy)  
Supersedes: none

## Objective

Define the exact folder layout Fleetwood must write so Vertical Builder can compile and deploy without missing data/assets.

Builder compiles only what is present in the export snapshot.  
If snapshot folders are empty or misplaced, output will be empty.

## Non-Negotiable Rules

- Export must be written to:
  - `gs://buzzpoint-sites-{env}/orgs/{orgId}/verticals/{verticalKey}/exports/{exportId}/`
- Export must include non-empty:
  - `content/`
  - `data/`
  - `static/`
  - `manifest.json`
- Builder does not read Firestore content at build time.
- Builder does not discover alternate folders.
- Builder does not transform CMS schema.

## Required Snapshot Layout

```text
gs://buzzpoint-sites-{env}/orgs/{orgId}/verticals/{verticalKey}/exports/{exportId}/
  manifest.json
  content/
    _index.md
    gymnasts/
      _index.md
      <slug>.md
    coaches/
      _index.md
      <slug>.md
    meets/
      _index.md
      <slug>.md
  data/
    org.json
    navigation.json
    site/
      settings.json
    hero.json
    home/
      sections.json
    calendar/
      events.json
    meta/
      site.json
  static/
    images/
      logo.jpg
      favicon.ico
      coaches/
        <image-files>
      gymnasts/
        <image-files>
    assets/
      <theme-overrides-if-any>
```

## Image Placement Rules (Important)

- All image binaries must be exported under `static/`.
- Preferred image root:
  - `static/images/...`
- Markdown/frontmatter image URLs must reference paths that exist under `static/`.
  - Example valid URLs:
    - `/images/logo.jpg`
    - `/images/coaches/mira-langford.jpg`
    - `/images/gymnasts/amelia-brooks.jpg`
- Do not place images under `content/` or `data/`.
- Do not rely on runtime external CMS URLs for required page imagery.

## Data File Format Rules

- JSON is supported and expected for this contract.
- Keep filenames and keys stable with template usage (`site.Data.*` paths).
- If switching from YAML to JSON, maintain equivalent structure:
  - `data/org.json` -> `site.Data.org`
  - `data/navigation.json` -> `site.Data.navigation`
  - `data/site/settings.json` -> `site.Data.site.settings`
  - `data/meta/site.json` -> `site.Data.meta.site`

## Manifest Minimum

`manifest.json` must include:

- `exportId`
- `orgId`
- `verticalKey`
- `templateKey`
- `env`
- `generatedAt`
- `sourceUpdatedAt`
- `contentHash`
- `assetHash`
- `files.markdownCount`
- `files.assetCount`

## Common Failure Modes (Seen)

- Snapshot prefix exists but zero blobs under `content/`, `data/`, `static/`.
- Export wrote to wrong bucket/env path.
- Export wrote markdown but omitted `static/images/*`.
- Data keys changed shape during YAML -> JSON transition.

## Validation Checklist (Fleetwood)

Before enqueueing Pub/Sub:

1. Verify export path exists for exact `exportId`.
2. Verify `content/`, `data/`, `static/` each contain files.
3. Verify `manifest.json` keys match payload fields.
4. Verify image references in markdown/frontmatter resolve to `static/` files.
5. Only then publish builder job.

## Valid Build Payload Example

```json
{
  "jobId": "vb_90587a32a797",
  "env": "sword",
  "orgId": "matthew-sword",
  "verticalKey": "gymnastics",
  "templateKey": "gymnastics",
  "exportId": "20260225T024104Z",
  "buildTarget": {
    "hostingProject": "bap-broadcast",
    "site": "matthew-sword"
  }
}
```

## Ownership Boundary Reminder

- Fleetwood owns export correctness and snapshot completeness.
- Builder owns compile/deploy from snapshot only.
- If snapshot is incomplete, builder must fail fast and write failed receipt.
