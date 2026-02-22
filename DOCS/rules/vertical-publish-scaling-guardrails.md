# Vertical Publish — Scaling Guardrails

Author: Matthew Sword  
Module: Gymnastics Vertical (applies to all verticals)  
Status: Required  
Last Updated: 2026-02-22

---

# 1. Purpose

This document defines mandatory scaling protections for the Vertical Publish architecture.

The goal:

Allow hundreds of sites to be built safely without:

- Retry storms
- Duplicate deploys
- Overwriting newer builds
- Firebase Hosting throttling
- Cross-environment contamination
- Cost explosions

These guardrails are non-optional for production environments.

---

# 2. Concurrency Controls

## 2.1 Per-Org Build Lock (Required)

Only one build per org per vertical may run at a time.

Lock document path:

orgs/<orgId>/verticalBuildLocks/<verticalKey>

Lock fields:

- jobId
- exportId
- lockedAt
- ttlSeconds

Rules:

- Builder must acquire lock before building.
- If lock exists and not expired, reject or requeue job.
- Lock must be released on success or failure.
- TTL must auto-expire in case of crash.

This prevents:

- Double builds
- Race conditions
- Export A overwriting Export B

---

## 2.2 Global Concurrency Cap (Required)

Builder service must limit total concurrent builds.

Recommended starting limits:

- Cloud Run max instances: 10–20
- One build per instance
- Allow backlog in Pub/Sub

This prevents:

- Firebase deploy throttling
- CPU/memory exhaustion
- Sudden cost spikes

---

# 3. Idempotency Requirements

Pub/Sub may deliver duplicate messages.

Builder must treat each job as idempotent.

## 3.1 Job-Level Idempotency

Receipt document path:

orgs/<orgId>/verticalBuildReceipts/<jobId>

If receipt exists with status = deployed:

- Return success immediately.
- Do not rebuild.

## 3.2 Export-Level Idempotency

If a job arrives with an exportId that is already deployed:

- Skip rebuild.
- Mark job as no-op success.

This prevents duplicate Firebase deploys.

---

# 4. Latest Export Wins Rule (Critical)

Scenario:

Export A is queued.
Export B is queued shortly after.
Export B is newer.

If Export A finishes after Export B, it must NOT overwrite Export B.

Required rule:

Each org stores:

orgs/<orgId>/verticals/<verticalKey>:
desiredExportId: "<latest>"

Builder must check:

If exportId != desiredExportId:
Cancel build early.
Mark receipt as stale.
Release lock.

This prevents:

- Older builds overwriting newer sites.
- Race-condition deploy regressions.

---

# 5. Hosting Deployment Strategy

## 5.1 Environment Isolation (Required)

- QA builds deploy only to QA Firebase project.
- PROD builds deploy only to PROD Firebase project.
- No cross-environment deploy allowed.

Builder must validate:

payload.env == service.env

Reject if mismatch.

---

## 5.2 Multi-Site Hosting Strategy (Recommended)

To support 100s of orgs:

- Use one Firebase project per environment.
- Use multiple Hosting sites within project.
- Map orgId → hosting site target.

Avoid:

- Creating one Firebase project per org.
- Cross-project deploy complexity.

---

# 6. Retry and Failure Handling

## 6.1 Pub/Sub Retry Awareness

Pub/Sub may retry on:

- Non-200 responses
- Timeout
- Instance crash

Builder must:

- Return 200 only after safe acceptance.
- Use jobId dedupe logic.
- Avoid side effects before lock acquisition.

---

## 6.2 Failure Recovery

On failure:

- Release org lock.
- Mark receipt status = failed.
- Log error summary.
- Allow new build with new jobId.

Do NOT leave lock stuck.

---

# 7. Export Cleanup (Orphan Prevention)

Phase 1:

- Full regeneration per export.
- Replace entire static build output.

Phase 2 (incremental mode):

Exporter must:

- Generate manifest of expected files.
- Detect files removed since last export.
- Ensure deleted content does not remain in site.

Without orphan cleanup:

- Deleted athletes will remain forever.
- Stale competitions will persist.

---

# 8. Asset Download Optimization

When scaling:

- Cache template inside builder container image.
- Download only org-specific content and assets.
- Avoid re-downloading static template files.

Optional future optimization:

- Compare asset hashes before re-downloading.

---

# 9. Resource Limits

Builder container should define:

- CPU limit
- Memory limit
- Timeout limit (e.g., 5–10 minutes)

Long-running builds must fail safely and release lock.

---

# 10. Observability Requirements

Each build must record:

- jobId
- orgId
- verticalKey
- exportId
- startedAt
- finishedAt
- status
- deployTarget
- error summary (if failed)

Without receipts, scaling is blind.

---

# 11. Forbidden Patterns

- Unlimited Cloud Run scaling without concurrency cap
- Deploying without per-org lock
- Ignoring duplicate Pub/Sub deliveries
- Allowing stale builds to overwrite newer builds
- Cross-environment bucket reads
- Cross-environment Firebase deploys
- Silent failure without receipt

---

# 12. Definition of Production-Ready

Vertical Publish is production-ready when:

- Per-org locking works
- Latest export wins logic works
- Global concurrency is capped
- Idempotency confirmed
- Receipts recorded
- Failed builds release locks
- 100 build jobs can queue without failure cascade

---

End of Document.
