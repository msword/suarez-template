# Handoff: Vertical Builder Service (First Handoff)

Date: 2026-02-25  
Owner: Fleetwood (Core API exporter), Builder Owner (compile/deploy runtime)  
Supersedes: `docs/handoff/backend-handoff-v3.md`

## Breaking Changes

- Runtime env source changed to `ENV` (previously `BUILDER_ENV` in local builder code).
- Canonical Pub/Sub payload uses `buildTarget.hostingProject` + `buildTarget.site`.
- Builder derives snapshot path from bucket/env/org/vertical/export IDs; no `snapshotUri` in canonical payload.

## Migration Notes

- Set `ENV` in all builder runtime environments.
- Ensure export snapshots are written to:
  - `gs://buzzpoint-sites-{env}/orgs/{orgId}/verticals/{verticalKey}/exports/{exportId}/`
- Update all publishers to send canonical payload.
- For local-only compile, set `buildTarget.site` to `local`.

## Delivery Model (Who/What/When/How)

- Who:
  - Core API owns snapshot export, manifest generation, and build-job enqueue.
  - Vertical Builder service owns compile/deploy execution only.
- What:
  - Builder consumes immutable snapshot exports and produces deployed static site output.
  - Builder remains schema-agnostic.
- When:
  - Any payload/manifest contract change must be documented in this handoff in the same PR.
  - Any builder runtime/lock/receipt behavior change must be documented before deploy.
- How:
  - Validate payload/env/manifest before build.
  - Build strictly from exported bucket snapshot.
  - Write deterministic receipts and release lock on all paths.

## Architecture Rules (Non-Negotiable)

- Builder is compile/deploy only.
- Builder does not read CMS Firestore schema documents for content.
- Builder does not transform CMS schema data.
- Core API does not run Hugo for SiteCMS publish.
- All builds are async via Pub/Sub.
- No cross-environment bucket access.
- No cross-environment deploy.

## Current Publish Flow (Source of Truth)

1. `POST /module/gymnastics/site/publish` (core API)
2. Core API exports workspace + writes `manifest.json`
3. Core API uploads export snapshot to:
   - `gs://buzzpoint-sites-{env}/orgs/{orgId}/verticals/{verticalKey}/exports/{exportId}/`
4. Core API publishes `vertical-builder__{env}` message (or fallback by infra policy)
5. Builder endpoint receives Pub/Sub push:
   - `POST /modules/vertical-builder`
6. Builder validates and executes:
   - lock -> download -> manifest verify -> `hugo --minify` -> deploy/local-output -> receipt -> unlock

## Pub/Sub Payload Contract

### Current (Canonical)

```json
{
  "jobId": "vb_<uuid>",
  "env": "sword|qa|prod|dev",
  "orgId": "<orgId>",
  "verticalKey": "gymnastics",
  "templateKey": "gymnastics",
  "exportId": "<exportId>",
  "buildTarget": {
    "hostingProject": "<firebase-project>",
    "site": "<hosting-site-target|local>"
  }
}
```

Rules:

- `env` must equal runtime `ENV`.
- `exportId` is immutable; builder does not infer latest.
- No secrets in message payload.

### Contract Diff (Before -> After)

- Removed: `buildTarget.snapshotUri`
- Added/Required: `buildTarget.hostingProject`
- Unchanged: `buildTarget.site` (supports `local` for no-deploy output)
- Runtime config: `BUILDER_ENV` -> `ENV`

### Invalid Example (Rejected 400)

```json
{
  "jobId": "vb_bad",
  "env": "qa",
  "orgId": "matthew-sword",
  "verticalKey": "gymnastics",
  "templateKey": "gymnastics",
  "exportId": "20260225T010025Z",
  "buildTarget": {
    "site": "matthew-sword"
  }
}
```

Reason: missing `buildTarget.hostingProject`.

## Snapshot Contract

Required contents:

- `content/`
- `data/`
- `static/`
- `manifest.json`

Manifest minimum keys:

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

## Locking and Receipts

Lock doc:

- `orgs/{orgId}/verticalBuildLocks/{verticalKey}`

Receipt doc:

- `orgs/{orgId}/verticalBuildReceipts/{jobId}`

Receipt status progression:

- `queued`
- `building`
- `deployed`
- `failed`

## Runtime Environment Notes

- Runtime environment is `ENV`.
- Export bucket default is `buzzpoint-sites-{ENV}` (overridable by `EXPORT_BUCKET`).
- `buildTarget.hostingProject` must match runtime `FIREBASE_PROJECT` unless `site=local`.
- If `site=local`, builder compiles and writes `vertical_builder/local_output/{jobId}/` and skips Firebase deploy.

## Validation

Manual command (valid):

```bash
PAYLOAD='{"jobId":"vb_bfa47f7556f8","env":"sword","orgId":"matthew-sword","verticalKey":"gymnastics","templateKey":"gymnastics","exportId":"20260225T010025Z","buildTarget":{"hostingProject":"local","site":"local"}}'
curl -X POST "http://localhost:8081/modules/vertical-builder" \
  -H "Content-Type: application/json" \
  -d "{\"message\":{\"data\":\"$(printf '%s' \"$PAYLOAD\" | base64)\"}}"
```

Expected:

- HTTP `200` accepted
- receipt transitions to `building` then `deployed` (or `failed`)
- lock released in all paths

Manual failure case:

- Send payload with mismatched `env` vs runtime `ENV`
- Expected HTTP `400` with env mismatch reason
