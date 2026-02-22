# Gymnastics Vertical — Hugo Reset Critical Rules v3

Author: Matthew Sword  
Persona: Codex Fleetwood  
Status: HARD RESET  
Date: 2026-02-22

---

## Non-Negotiable Rules

1. One vocabulary system only.
2. Plural section naming only.
3. Layout folder name must exactly match section name.
4. No duplicate content folders.
5. No singular and plural versions of the same section.
6. Do not use `athletes` when `gymnasts` is canonical.
7. Do not use `competition` singular when `competitions` is canonical.
8. Hugo must build locally before export/deploy.

## Canonical Section Names

- `gymnasts`
- `coaches`
- `competitions`
- `meets`

Forbidden:

- `athlete`
- `athletes`
- `competition` (singular)
- `coach` (singular folder)

## Required Hugo Structure

```text
/config.yaml

/content
  /gymnasts
  /coaches
  /competitions
  /meets

/layouts
  /gymnasts
  /coaches
  /competitions
  /meets
  /_default

/static
/assets
```

No additional content roots are permitted.

## Required Front Matter Rules

- `draft` must be `false`.
- `status` must be `active` to render in list pages.
- Slug must derive from the entity name.
- `federationId` must be unique.
- Seeder must be idempotent.

## Required list.html Pattern

Use this modern Hugo approach:

```go-html-template
{{ define "main" }}

<h1>{{ .Title }}</h1>

{{ range where .RegularPages "Params.status" "active" }}
  <div>
    <a href="{{ .RelPermalink }}">{{ .Title }}</a>
  </div>
{{ end }}

{{ end }}
```

Do not use:

- `.Pages`
- `.Data.Pages`
- `.Site.Pages`

## Required single.html Pattern

```go-html-template
{{ define "main" }}

<h1>{{ .Title }}</h1>

{{ .Content }}

<ul>
  <li>Age: {{ .Params.age }}</li>
  <li>Level: {{ .Params.level }}</li>
  <li>Gender: {{ .Params.gender }}</li>
  <li>Federation ID: {{ .Params.federationId }}</li>
</ul>

{{ end }}
```

## Firestore Reset Rules

Reset collections:

- `gymnasts`
- `coaches`
- `competitions`
- `meets`

Seeder requirements:

1. Query existing by `federationId`.
2. Upsert instead of blind create.
3. Default `status` to `active`.
4. Default `draft` to `false`.

## Export Rules

1. Write to `/content/<section>/` only.
2. Overwrite entire section on export.
3. Remove orphaned files.
4. Do not mix previous export folders.
5. Do not create both singular and plural variants.

Before export write:

- Delete `content/gymnasts`
- Delete `content/coaches`
- Delete `content/competitions`
- Delete `content/meets`

## Forbidden Patterns

- Duplicate folder naming.
- Singular/plural drift.
- Multiple content roots.
- Exporting to `sitecms-export` and `content` simultaneously.
- Leaving old content in place.
- Generating layout files dynamically.

The Hugo project must remain deterministic.
