# Gymnastics SiteCMS API and Theme Contract

## Scope
This document defines the SiteCMS API surface and plain-theme rendering constraints for the gymnastics template.

## API Base
- Prefix: `/module/gymnastics`
- Auth: `Authorization: Bearer <id_token>`
- Org scope: `X-Org-Id: <org_id>`
- Role: `admin` required for all SiteCMS routes

## Endpoints

### GET `/site`
Returns the site snapshot.

Response shape:
```json
{
  "status": "success",
  "data": {
    "heroSlides": [],
    "navigation": {},
    "siteSettings": {},
    "customPages": []
  }
}
```

### POST `/site/hero`
Creates a hero slide.

### PUT `/site/hero/:id`
Updates a hero slide.

### DELETE `/site/hero/:id`
Deletes a hero slide.

### PUT `/site/navigation`
Replaces navigation items.

### PUT `/site/settings`
Upserts site settings.

### GET `/site/pages`
Lists custom pages.

### GET `/site/pages/by-slug/:slug`
Fetches one custom page by slug for editor loading.

### POST `/site/pages`
Creates a custom page.

Payload:
```json
{
  "title": "Summer Camp",
  "slug": "summer-camp",
  "bodyMarkdown": "Camp registration details.",
  "active": true
}
```

### PUT `/site/pages/:id`
Updates a custom page.

### DELETE `/site/pages/:id`
Deletes a custom page.

### POST `/site/export`
Exports a normalized Hugo workspace (content/data/config) without running Hugo build or deploy.

Response includes:
- `exportPath`
- `generatedAt`
- `orgId`

### POST `/site/publish`
Queues async publish.

Success response:
```json
{
  "status": "success",
  "data": {
    "job_id": "site_publish_abc123",
    "status": "queued"
  }
}
```

Lock conflict response:
- HTTP `409`
- error code: `PublishInProgress`

## Firestore Shape
Org-scoped module path:
- `orgs/{org_id}/modules/gymnastics/site/root`

Subcollections:
- `hero_slides`
- `navigation` (doc `main`)
- `site_settings` (doc `config`)
- `coaches`
- `athletes`
- `competitions`
- `pages`

Custom page document keying:
- `pages/{slug}` where `slug` is the exact `__c` path segment.
- Example: `/__c/summer-camp` maps to `pages/summer-camp`.

Custom pages are rendered to static routes under:
- `/__c/{slug}`
- Reserved slugs are blocked (`coaches`, `gymnasts`, `meets`, `site`, `__c`, etc.)
- Duplicate slugs are rejected per org

Publish lock + receipts:
- `orgs/{org_id}/site/publish_lock`
- `orgs/{org_id}/site/root/publish_receipts/{job_id}`

## Plain Theme Contract
The gymnastics theme is intentionally stripped to plain HTML:
- No CSS includes
- No JS includes
- No jQuery
- No lightbox/wow/animation libraries
- No image rendering in templates
- No asset dependency required for render

Template behavior:
- Home reads hero slides from front matter: `.Params.hero.slides`
- Navigation reads from `data/navigation.yaml`
- Custom pages are generated to `content/__c/{slug}.md`
- Rendering is semantic HTML only (`header`, `nav`, `main`, `section`, `article`, `ul`, `li`, `p`, `a`)

## Postman Collection
- `postman/modules/gymnastics_site_cms_collection.json`

## Local Build Script
For local one-command build + preview with clean handoff:
1. API exports workspace (`POST /site/export`)
2. Local Hugo builds presentation output

```bash
scripts/build_sitecms_local.sh --org <org_id> --token "<id_token>"
```

Build-only mode:

```bash
scripts/build_sitecms_local.sh --org <org_id> --token "<id_token>" --build-only
```

Output path:
- `generated/sitecms-local/<org_id>/public`
