# Gymnastics Module Backend Handoff

> Superseded by `docs/modules/gynastics/backend-handoff-v2.md` for coaches + publish + Suarez SSG flow.

Branch: `feature/gymnastics-module`  
Owner: Codex Fleetwood  
Scope: Vertical engine under `/modules/gymnastics` only

## 1. What Was Delivered

New vertical module added with isolated route/service/schema/model/seed implementation:

- `modules/gymnastics/routes.py`
- `modules/gymnastics/service.py`
- `modules/gymnastics/schema.py`
- `modules/gymnastics/models.py`
- `modules/gymnastics/seed.py`

Module blueprint is registered in app startup:

- `app/__init__.py`

Base path:

- `/module/gymnastics`

## 2. Feature Flag Contract

All module routes are gated by org-level module flag:

```json
{
  "modules": {
    "gymnastics": true
  }
}
```

Behavior:

- If disabled/missing, routes return `403` with `FeatureDisabled`.

Note:

- Seed route auto-enables `modules.gymnastics=true` before seeding.

## 3. Firestore Storage Layout

The module now uses org-contained module paths:

- `orgs__<env>/{orgId}/modules/gymnastics/gymnasts/{gymnastId}`
- `orgs__<env>/{orgId}/modules/gymnastics/meets/{meetId}`
- `orgs__<env>/{orgId}/modules/gymnastics/meetSessions/{sessionId}`
- `orgs__<env>/{orgId}/modules/gymnastics/scores/{scoreId}`
- `orgs__<env>/{orgId}/modules/gymnastics/meta/seed_run`

Org isolation is enforced by path boundary first, and also retained in payload as `orgId`.

## 4. Route Inventory

### Gymnasts

- `GET /module/gymnastics/gymnasts?search=&page=&limit=`
- `POST /module/gymnastics/gymnasts`
- `GET /module/gymnastics/gymnasts/:id`
- `PUT /module/gymnastics/gymnasts/:id`

### Meets

- `GET /module/gymnastics/meets?page=&limit=`
- `POST /module/gymnastics/meets`
- `GET /module/gymnastics/meets/:id`

### Meet Sessions

- `POST /module/gymnastics/meets/:id/sessions`
- `GET /module/gymnastics/meets/:id/sessions?page=&limit=`

### Scores

- `POST /module/gymnastics/scores`
- `GET /module/gymnastics/scores?meetId=&page=&limit=`
- `GET /module/gymnastics/scores?gymnastId=&page=&limit=`

### Seed (one-time)

- `POST /module/gymnastics/seed`
- Optional override: `POST /module/gymnastics/seed?force=true`

Seed guard:

- First run creates marker doc `orgs/{orgId}/modules/gymnastics/meta/seed_run`
- Later runs return `409 AlreadySeeded` unless `force=true`

## 5. Score Idempotency

Score writes are deterministic and retry-safe:

- Document ID: `{orgId}_{meetId}_{gymnastId}_{session}`
- Write mode: `set(..., merge=True)`

Guarantees:

- No duplicate score docs for same org/meet/gymnast/session tuple
- Safe overwrite for re-import/reprocess

## 6. Validation Rules

### Gymnast

- `gender`: `male | female`
- `status`: `active | archived`
- `level`, `age`: integer `>= 1`

### Meet

- Requires `name`, `location`, `startDate`, `endDate`
- `endDate >= startDate`

### Session

- Requires `session`, `level`, `division`
- `level` integer `>= 1`

### Scores

Required:

- `meetId`, `gymnastId`, `session`, `level`, `division`, `events`

Event validation:

- Allowed keys are gender-specific
- Unknown event keys rejected
- Unknown event field keys rejected
- `total` required decimal, non-negative, `<= 20`
- `difficulty` and `execution` optional, decimal when present
- `placement` required integer `>= 1`
- `allAround.total` optional

## 7. Gender Event Configuration

Defined centrally in `modules/gymnastics/models.py`:

```python
EVENTS_BY_GENDER = {
    "male": ["floor", "pommel", "rings", "vault", "pbars", "highbar"],
    "female": ["vault", "bars", "beam", "floor"],
}
```

No event list hardcoded across route handlers.

## 8. Seed Data Shape

`modules/gymnastics/seed.py` provisions:

- 12 gymnasts
- 2 meets
- 1 session
- 10 score records

Also records a seed-run summary in `orgs/{orgId}/modules/gymnastics/meta/seed_run` for auditability.

## 9. Postman Module Collection

Collection file:

- `postman/modules/gymnastics_module_collection.json`

Contains:

- Authenticated requests for all module routes
- Seed flow (normal + force)
- Variable extraction scripts for `meetId` and `gymnastId`
- Score upsert payload sample

## 10. Required Firestore Indexes (Manual)

Create the following composite indexes:

- `meetSessions`: `meetId ASC, session ASC`
- `scores`: `meetId ASC, updatedAt DESC`
- `scores`: `gymnastId ASC, updatedAt DESC`

Notes:

- `gymnasts` list is ordered by `name` within org-scoped subcollection path.
- `meets` list is ordered by `startDate DESC` within org-scoped subcollection path.

## 11. Operational Notes

- Module is isolated; no changes were made to `CreditService` or compliance routing.
- Route auth pattern follows existing `@auth_required` + `@org_guard` convention.
- Seed route is intended for one-time bootstrap per org, with explicit force override.
