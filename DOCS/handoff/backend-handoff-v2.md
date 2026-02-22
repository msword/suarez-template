# Gymnastics Module Backend Handoff v2

Branch: `feature/gymnastics-module`  
Owner: Codex Fleetwood  
Scope: Vertical engine + SSG pipeline for gymnastics

## 1. Context

Gymnastics v2 extends the first vertical module with:

- Gymnast roster management
- Coach profiles (Markdown + inline HTML)
- Meet + session management
- Idempotent score tracking
- Static site generation publish flow (Suarez template)

Module path:

- Source: `modules/gymnastics`
- API prefix: `/module/gymnastics`

## 2. Route Contract (v2)

All routes are auth + org guarded and module flag gated (`org.modules.gymnastics == true`), except seed bootstrap which can set the module flag.

### Gymnasts

- `GET /module/gymnastics/gymnasts`
- `POST /module/gymnastics/gymnasts`
- `PUT /module/gymnastics/gymnasts/:id`

### Coaches

- `GET /module/gymnastics/coaches`
- `POST /module/gymnastics/coaches`
- `PUT /module/gymnastics/coaches/:id`

### About / Hours

- `GET /module/gymnastics/about`
- `PUT /module/gymnastics/about`
- `GET /module/gymnastics/hours`
- `PUT /module/gymnastics/hours`
- `GET /module/gymnastics/site-settings`
- `PUT /module/gymnastics/site-settings`

### Meets / Sessions

- `GET /module/gymnastics/meets`
- `POST /module/gymnastics/meets`
- `POST /module/gymnastics/meets/:id/sessions`
- `GET /module/gymnastics/meets/:id/sessions`

### Scores

- `POST /module/gymnastics/scores`
- `GET /module/gymnastics/scores?meetId=`
- `GET /module/gymnastics/scores?gymnastId=`

### Publish

- `POST /module/gymnastics/publish`

### Seed

- `POST /module/gymnastics/seed`
- `POST /module/gymnastics/seed?force=true`

## 3. Firestore Storage Layout (Contained)

All gymnastics data is contained under:

- `orgs__<env>/{orgId}/modules/gymnastics/gymnasts/{gymnastId}`
- `orgs__<env>/{orgId}/modules/gymnastics/coaches/{coachId}`
- `orgs__<env>/{orgId}/modules/gymnastics/meets/{meetId}`
- `orgs__<env>/{orgId}/modules/gymnastics/meetSessions/{sessionId}`
- `orgs__<env>/{orgId}/modules/gymnastics/scores/{scoreId}`
- `orgs__<env>/{orgId}/modules/gymnastics/meta/about`
- `orgs__<env>/{orgId}/modules/gymnastics/meta/hours`
- `orgs__<env>/{orgId}/modules/gymnastics/meta/site_settings`
- `orgs__<env>/{orgId}/modules/gymnastics/meta/seed_run`

Every document includes `orgId`.

## 4. Data Contracts

### Gymnasts

```json
{
  "id": "auto",
  "orgId": "string",
  "name": "string",
  "gender": "male | female",
  "level": "number",
  "age": "number",
  "federationId": "string",
  "bioMarkdown": "string",
  "profileImage": "string",
  "images": ["string"],
  "status": "active | archived",
  "createdAt": "timestamp",
  "updatedAt": "timestamp"
}
```

### Coaches

```json
{
  "id": "auto",
  "orgId": "string",
  "name": "string",
  "pageDesc": "string",
  "bioMarkdown": "string",
  "displayOrder": "number",
  "status": "active | archived",
  "createdAt": "timestamp",
  "updatedAt": "timestamp"
}
```

### Meets

```json
{
  "id": "auto",
  "orgId": "string",
  "name": "string",
  "location": "string",
  "startDate": "date",
  "endDate": "date",
  "createdAt": "timestamp"
}
```

### Meet Sessions

```json
{
  "id": "auto",
  "orgId": "string",
  "meetId": "string",
  "session": "string",
  "level": "number",
  "division": "string"
}
```

### Scores (idempotent)

Deterministic ID:

- `{orgId}_{meetId}_{gymnastId}_{session}`

Write mode:

- `set(..., merge=True)`

### About (meta)

```json
{
  "title": "string",
  "pageDesc": "string",
  "aboutMarkdown": "string",
  "updatedAt": "timestamp"
}
```

### Hours (meta)

```json
{
  "timezone": "string",
  "hours": [
    {
      "day": "string",
      "open": "string",
      "close": "string",
      "closed": "boolean"
    }
  ],
  "updatedAt": "timestamp"
}
```

### Site Settings (meta)

```json
{
  "siteTitle": "string",
  "tagline": "string",
  "heroText": "string",
  "theme": {
    "accent": "string",
    "accentInk": "string",
    "bg": "string",
    "surface": "string",
    "text": "string",
    "muted": "string",
    "border": "string"
  },
  "navigation": [
    {"label": "string", "url": "string"}
  ],
  "updatedAt": "timestamp"
}
```

## 5. Gender Event Validation

Central config:

```python
EVENTS_BY_GENDER = {
    "male": ["floor", "pommel", "rings", "vault", "pbars", "highbar"],
    "female": ["vault", "bars", "beam", "floor"]
}
```

Validation:

- Reject unknown events
- Reject events invalid for gymnast gender
- Allow nullable `difficulty` / `execution`
- Enforce decimal sanity and `placement >= 1`

## 6. Markdown Handling

- Firestore stores structured fields + raw markdown only
- No frontmatter stored in Firestore
- No sanitization/escaping transform of body markdown for trusted org content

## 7. SSG Publish Flow

`POST /module/gymnastics/publish` does:

1. Ensures template assets are present
2. Reads gymnasts/coaches/meets/scores from module collections
3. Generates files:

- `generated/content/gymnasts/*.md`
- `generated/content/coaches/*.md`
- `generated/content/meets/*.md`
- `generated/content/about/_index.md`
- `generated/data/scores/{meetId}.json`
- `generated/data/site/settings.json`

4. Optional command execution:

- If `runBuild=true`: `hugo --source /generated --destination /output`
- If `runDeploy=true`: `firebase deploy --only hosting:{orgSlug}`

## 8. Suarez Template Location

Template assets are staged under:

- `templates/gymnastics/suarez`

Template rule:

- Template contains structure only (`layouts`, `partials`, `static`, `theme.toml`).
- Template must not contain real org content (`content/` is forbidden here).
- Template must not contain hardcoded org image assets (`static/images` is forbidden here).
- Template must not depend on jQuery/Bootstrap-era asset bundles from prior site exports.

Theme source assets can be hydrated from:

- `themes.zip`

Runtime fallback:

- If gymnast `profileImage` is missing, publish writes and templates use `/assets/default-profile.svg`.

## 9. Seed v2

Seed now includes:

- 12 gymnasts (with `bioMarkdown`)
- 3 coaches (including Casimiro sample with inline HTML markdown)
- 2 meets
- 1 session
- 10 score records

## 10. Postman v2

Collection:

- `postman/modules/gymnastics_module_collection.json`

Includes coaches and publish routes.

## 11. Index Guidance

Recommended indexes for high-volume query paths:

- `gymnasts`: `orgId ASC, name ASC`
- `coaches`: `orgId ASC, displayOrder ASC`
- `meets`: `orgId ASC, startDate DESC`
- `scores`: `orgId ASC, meetId ASC`
- `scores`: `orgId ASC, gymnastId ASC`

Note: the current contained subcollection implementation can operate without these composites for low/medium volume because read/filter/sort fallback is used in service methods.

## 12. Non-goals

Still excluded in v2:

- AI ingestion
- Charts
- Parent linking
- Media gallery
- Segmentation integration
- Billing integration
