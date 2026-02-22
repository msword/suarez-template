# Vertical Publish Architecture — Bucket + Builder (Hugo SSG)

Author: Matthew Sword  
Module: Gymnastics Vertical (applies to all verticals)  
Status: Draft → Adopt  
Last Updated: 2026-02-22

---

# 1. Purpose

Define the canonical "Vertical Publish" pipeline for static site generation (SSG) verticals.

This pipeline supports any Hugo-based template and any vertical (gymnastics first).

Goals:

- Environment-safe
- Multi-tenant
- Deterministic builds
- No runtime bucket dependencies for images (Pattern A)
- Async build execution via Pub/Sub
- Clear separation between "export content" and "build & deploy"

---

# 2. High-Level Flow

1. Vertical Publish writes content + assets to an org-scoped site bucket path (only updated files; lastUpdatedAt = X)

2. Vertical Publish enqueues a Pub/Sub message to `vertical-builder` topic

3. Builder service receives Pub/Sub push at:

POST /modules/vertical-builder

4. Builder assembles Hugo workspace from bucket snapshot + template

5. Builder runs Hugo build

6. Builder deploys static HTML to Firebase Hosting (env-specific project)

---

# 3. Components

## 3.1 Vertical Publish (Exporter)

Responsibilities:

- Pull Firestore CMS snapshot for org + template
- Generate markdown into Hugo content structure
- Generate data files (YAML/JSON) used by layouts
- Resolve all referenced assets (logos/images) and stage them (Pattern A)
- Write staged content + assets to org site bucket
- Publish build request to Pub/Sub topic

Must NOT:

- Run hugo build
- Deploy to Firebase
- Perform runtime rendering

Output is an export snapshot, not a website.

## 3.2 Vertical Builder (SSG Builder)

Responsibilities:

- Receive build request via Pub/Sub push
- Validate request (env, org, template)
- Acquire per-org build lock
- Download export snapshot from bucket
- Assemble Hugo workspace (template + content + assets)
- Run hugo build
- Deploy to Firebase Hosting (env-specific)
- Write build receipt + clear lock

Must NOT:

- Mutate Firestore CMS content
- Invent content fields
- Modify schema contracts

---

# 4. Storage Model (Buckets)

## 4.1 Site Export Bucket (Per Environment)

Each environment has an export bucket:

- QA: gs://buzzpoint-sites-qa
- PROD: gs://buzzpoint-sites-prod
- DEV/SWORD: gs://buzzpoint-sites-dev

No cross-environment writes.

## 4.2 Canonical Export Path

All vertical exports write to:

gs://<sites-bucket>/orgs/<orgId>/verticals/<verticalKey>/exports/<exportId>/

Where:

- verticalKey: gymnastics, legion, etc.
- exportId: timestamp or UUID, unique per publish attempt

Export snapshot contains:

- content/ (markdown)
- data/ (yaml/json)
- static/images/ (Pattern A bundled assets)
- manifest.json (export metadata)

Example:

gs://buzzpoint-sites-qa/orgs/matthew-sword/verticals/gymnastics/exports/2026-02-22T14-05-33Z/

## 4.3 Latest Pointer (Optional)

Optionally store:

gs://.../exports/latest.json

Which points to the most recent exportId.

This is not required if Pub/Sub payload includes exportId.

---

# 5. Export Manifest (Required)

Each export must include:

manifest.json

Minimum fields:

{
"exportId": "2026-02-22T14-05-33Z",
"orgId": "matthew-sword",
"verticalKey": "gymnastics",
"templateKey": "gymnastics-suarez",
"env": "qa",
"contentHash": "<hash>",
"assetHash": "<hash>",
"generatedAt": "ISO8601",
"sourceUpdatedAt": "ISO8601",
"files": {
"markdownCount": 42,
"assetCount": 18
}
}

The manifest makes builds deterministic and auditable.

---

# 6. Pub/Sub Contract

## 6.1 Topic

vertical-builder\_\_{env}

Examples:

- vertical-builder\_\_qa
- vertical-builder\_\_prod

## 6.2 Pub/Sub Payload

{
"jobId": "vb_abc123",
"env": "qa",
"orgId": "matthew-sword",
"verticalKey": "gymnastics",
"templateKey": "gymnastics-suarez",
"exportId": "2026-02-22T14-05-33Z",
"buildTarget": {
"hostingProject": "buzzpoint-gymnastics-qa",
"site": "default"
}
}

No secrets in payload.

---

# 7. Builder Endpoint Contract

Pub/Sub push target:

POST /modules/vertical-builder

Rules:

- Must verify Pub/Sub signature / OIDC token (env-specific)
- Must reject missing orgId, verticalKey, templateKey, exportId
- Must validate env matches service env
- Must be idempotent (jobId as dedupe key)

Response: 200 only if accepted.

---

# 8. Workspace Assembly (Builder)

Builder creates a clean workspace:

/tmp/build/<jobId>/
template/ (checked out or bundled in container)
content/ (downloaded from export)
data/ (downloaded from export)
static/images/ (downloaded from export)
config.yaml (template base + org overrides)

Then runs:

hugo --minify

Output:

/tmp/build/<jobId>/public

Then deploys public/ to Firebase Hosting.

---

# 9. Deployment Rules

Deployment must be environment-specific:

- QA builds deploy only to QA Firebase Hosting project
- PROD builds deploy only to PROD Firebase Hosting project

No cross-env deploy.

---

# 10. Locking and Idempotency

Builder must use:

- per-org build lock
- per-job dedupe

Suggested lock doc:

orgs/<orgId>/verticalBuildLocks/<verticalKey>

Lock fields:

- jobId
- lockedAt
- ttlSeconds

If lock exists and not expired, reject or reschedule.

Job dedupe:

- store receipt keyed by jobId
- if jobId already completed, return success without rebuilding

---

# 11. Incremental Writes (Exporter)

Exporter SHOULD avoid rewriting unchanged files.

Rules:

- If record updatedAt <= lastExportedAt, do not rewrite markdown
- If asset hash unchanged, do not rewrite asset

However:

Phase 1 may do full regeneration (safe mode) until stable.

Incremental mode requires:

- lastExportedAt pointer
- hashing
- deletion/orphan detection

---

# 12. Receipts (Required)

Builder writes receipts to Firestore:

orgs/<orgId>/verticalBuildReceipts/<jobId>

Receipt fields:

- jobId
- env
- verticalKey
- templateKey
- exportId
- status: queued | building | deployed | failed
- startedAt
- finishedAt
- deployedAt
- deployTarget
- error (if failed)

This is required for audit and operational support.

---

# 13. Failure Handling

If build fails:

- Lock must be released
- Receipt must mark failed
- Error should be recorded (summary + stack trace reference)
- Retrying must respect dedupe rules (new jobId or explicit retry token)

---

# 14. Non-Negotiable Rules

- No secrets in Pub/Sub payload
- No cross-env bucket reads
- No cross-env Firebase deploy
- No runtime image fetch from buckets (Pattern A)
- Template remains canonical and reusable
- Export is deterministic and traceable via manifest

---

End of Document.
