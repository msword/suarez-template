# Decision Log: Vertical Builder Contract Alignment

Date: 2026-02-25  
Owner: Builder Owner

## Decision

Adopt a single builder runtime contract:

- Runtime env comes from `ENV`
- Pub/Sub payload uses `buildTarget.hostingProject` + `buildTarget.site`
- Snapshot location is derived from `env/orgId/verticalKey/exportId`
- Receipt states are explicit (`queued`, `building`, `deployed`, `failed`)

## Context

Builder implementations diverged between `snapshotUri`-based and derived-path payload handling. Runtime env naming also diverged (`BUILDER_ENV` vs `ENV`), causing integration confusion and failed local tests.

## Alternatives considered

1. Keep dual payload support indefinitely (`snapshotUri` and derived-path).
2. Continue using `BUILDER_ENV` in builder runtime.
3. Standardize on one contract and enforce strict validation.

## Chosen approach

Option 3.

- Enforce `ENV` for runtime environment.
- Require `buildTarget.hostingProject` and `buildTarget.site`.
- Derive snapshot bucket path from runtime/env payload identity fields.
- Keep `site=local` as explicit local output mode (no Firebase deploy).

## Consequences / tradeoffs

- Pros:
  - Deterministic and auditable snapshot lookup.
  - Cleaner producer/consumer contract.
  - Reduced local/runtime ambiguity.
- Cons:
  - Requires publisher updates where `snapshotUri` payloads are still emitted.
  - Stricter validation may reject legacy messages until migrated.
