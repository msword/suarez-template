# Vertical Builder Runtime

## HTTP contract

- Method: `POST`
- Path: `/modules/vertical-builder`
- Body:

```json
{
  "message": {
    "data": "<base64-encoded JSON>"
  }
}
```

Behavior:

- Invalid payload or env mismatch: HTTP `400`
- Accepted payload: HTTP `200` immediately
- Build runs asynchronously in a single in-process worker (`max_workers=1`)

## Module layout

- `app.py` (only HTTP route)
- `builder_service.py` (build orchestration)
- `lock_service.py`
- `receipt_service.py`
- `bucket_service.py`
- `deploy_service.py`
- `config.py`

## Build flow

`handle_build_job(payload)` performs:

1. Acquire lock: `orgs/{orgId}/verticalBuildLocks/{verticalKey}`
2. Build snapshot path from `env/orgId/verticalKey/exportId`:
   - `gs://{EXPORT_BUCKET}/orgs/{orgId}/verticals/{verticalKey}/exports/{exportId}`
3. Download snapshot from bucket
3. Verify `manifest.json` before build
4. Assemble workspace (`content/`, `data/`, `static/`, `themes/gymnastics/`, `config.yaml`)
5. Run `hugo --minify`
6. Deploy only `workspace/public` with:
   - `firebase deploy --only hosting:{site} --project {FIREBASE_PROJECT}`
7. Write receipt: `orgs/{orgId}/verticalBuildReceipts/{jobId}`
8. Release lock on success or failure

Special case:
- If `buildTarget.site == "local"`, Firebase deploy is skipped and build output is written to `vertical_builder/local_output/{jobId}/`.
- `buildTarget.hostingProject` is still required, but not used for `site=local`.

## Environment variables

Required:

- `ENV`
- `FIREBASE_PROJECT`

Optional:

- `EXPORT_BUCKET` (default: `buzzpoint-sites-{ENV}`)
- `VERTICAL_THEMES_ROOT` (default: `vertical_builder/themes`)
- `VERTICAL_BASE_CONFIG` (default: `vertical_builder/config/base-config.yaml`)
- `VERTICAL_LOCK_TTL_SECONDS` (default: `900`)
- `VERTICAL_WORKSPACE_ROOT` (default: `vertical_builder/workspaces`)

## Workspace persistence

Builder now persists every run under:

- `vertical_builder/workspaces/{jobId}/snapshot/`
- `vertical_builder/workspaces/{jobId}/workspace/`

These directories are intentionally retained for inspection and Hugo iteration.

## Payload contract

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

Receipt status progression:
- `queued`
- `building`
- `deployed`
- `failed`

## Cloud Run

Deploy with concurrency `1`.
Recommended startup command:

```bash
gunicorn -b :8080 -w 1 -k gthread --threads 1 vertical_builder.app:app
```
