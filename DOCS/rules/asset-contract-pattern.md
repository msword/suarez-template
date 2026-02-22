# Gymnastics Module — Asset Contract (Pattern A: Bundle at Build Time)

Author: Matthew Sword  
Module: Gymnastics Vertical  
Status: Active  
Last Updated: 2026-02-22

---

# 1. Purpose

Define the canonical asset strategy for Gymnastics static site generation using Pattern A:

All images and logos are bundled into the Hugo site at build time and served from Firebase Hosting.  
The deployed site must not fetch images from buckets at runtime.

This contract governs:

- Where assets live (source of truth)
- How content references assets
- How builds assemble assets into Hugo /static
- Naming conventions
- Environment isolation
- Update behavior (idempotency and caching)

---

# 2. Pattern A Summary

## Runtime Behavior (Deployed Site)

Images are served from Firebase Hosting:

- /images/...
- /assets/... (theme assets)

There are no runtime calls to GCS or Firebase Storage.

## Build-Time Behavior

Build worker or CI pipeline:

1. Reads Firestore snapshot (content and config)
2. Resolves required assets
3. Downloads assets from the correct environment bucket
4. Writes assets into Hugo static/
5. Runs hugo --minify
6. Deploys /public to Firebase Hosting

The bucket is a source of truth, not a runtime dependency.

---

# 3. Asset Source of Truth

Assets are stored in dedicated environment buckets.

QA:
gs://buzzpoint-assets-qa

PROD:
gs://buzzpoint-assets-prod

DEV/SWORD:
gs://buzzpoint-assets-dev

Environment isolation is mandatory.

No cross-environment reads or writes.

---

# 4. Bucket Path Conventions

All assets must be scoped by org and module:

gs://<bucket>/orgs/<orgId>/modules/gymnastics/<assetType>/<filename>

Canonical assetType folders:

- branding/ (logos, favicons)
- hero/ (carousel slides)
- coaches/ (coach photos)
- gymnasts/ (gymnast photos)
- gallery/ (future)
- documents/ (future)

Example:

gs://buzzpoint-assets-qa/orgs/matthew-sword/modules/gymnastics/branding/logo.png
gs://buzzpoint-assets-qa/orgs/matthew-sword/modules/gymnastics/hero/chalkup.jpg
gs://buzzpoint-assets-qa/orgs/matthew-sword/modules/gymnastics/coaches/casimiro-suarez.jpg

---

# 5. How Content References Assets

Firestore and markdown content must NOT store absolute bucket URLs.

Two supported approaches:

## Option A — Store site-relative paths

Example:

{
"logoPath": "/images/branding/logo.png",
"heroSlides": [
{ "imagePath": "/images/hero/chalkup.jpg" }
]
}

## Option B — Store assetId (recommended long-term)

Example:

{
"logoAssetId": "asset_logo_001",
"heroSlides": [
{ "imageAssetId": "asset_hero_003" }
]
}

During export/build, assetId resolves to the correct local static path.

One strategy must be chosen and enforced consistently.

---

# 6. Hugo Target Path Conventions

During build, assets are copied into Hugo static/ and must land in:

static/images/branding/
static/images/hero/
static/images/coaches/
static/images/gymnasts/

Final deployed URLs:

/images/branding/<file>
/images/hero/<file>
/images/coaches/<file>
/images/gymnasts/<file>

---

# 7. Build Assembly Rules (Required)

Build process must:

1. Create clean Hugo workspace
2. Remove previously generated static/images folders
3. Download required assets from correct environment bucket
4. Place assets into proper Hugo static directories
5. Ensure content references match target paths
6. Run Hugo build
7. Deploy /public

Phase 1 uses full regeneration to prevent orphan files.

Incremental sync is future enhancement.

---

# 8. Idempotency and Updates

## Asset Idempotency

Uploading the same asset should either:

- Overwrite the same bucket path, OR
- Generate a new hashed filename

Build must be deterministic:

Identical Firestore snapshot + identical bucket contents = identical /public output.

## Score Idempotency Clarification

Scores are idempotent per:

- gymnast
- meet
- event
- year

However, AI ingestion may correct prior values.

Therefore:

Score records must support update.
Idempotent means no duplicate keys.
It does NOT mean immutable.

---

# 9. Filename Strategy (Cache Safe)

Two allowed strategies:

## Strategy 1 — Stable filenames

logo.png
chalkup.jpg

Pros:
Simple

Cons:
May require cache-control configuration

## Strategy 2 — Hashed filenames (recommended)

logo.8f31c2.png
chalkup.193aab.jpg

Pros:
Safe cache busting
Deterministic updates

Cons:
Requires reference updates when file changes

Recommendation:
Use hashed filenames for hero, coaches, and gymnasts.
Logo may remain stable if caching headers are controlled.

---

# 10. Asset Upload Rules

Uploads must:

- Be org-scoped
- Be environment-scoped
- Be validated (file type, size limits)
- Be stored under canonical bucket path

If using assetId resolution, metadata must include:

- assetId
- orgId
- env
- bucketPath
- targetPath (site-relative)
- contentType
- sizeBytes
- hash (optional)
- createdAt
- updatedAt

---

# 11. Security Rules

- Bucket write permissions must not be public
- No cross-org asset access
- Only build workers and authorized admin services may read bucket objects
- Public access happens through Firebase Hosting only

---

# 12. Operational Verification Checklist

Before deploying Pattern A:

- Assets exist in correct environment bucket
- Snapshot includes correct image references
- Build copies files into Hugo static/images
- hugo server renders images locally
- Deployed site serves images from Hosting
- No external bucket URLs exist in rendered HTML

---

# 13. Forbidden Patterns

- Storing bucket URLs in content
- Linking directly to GCS in HTML
- Mixing QA and PROD buckets
- Leaving stale files in static/images
- Forking template per org to handle assets differently

---

End of Document.
