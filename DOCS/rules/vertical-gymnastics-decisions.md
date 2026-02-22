# Gymnastics Vertical — Architectural Decisions

## Decision 001 — Static Site Generation

We are using:

Hugo + Tailwind + Swiper

Reason:

- Low runtime cost
- High performance
- SEO friendly
- Firebase-compatible
- No SSR complexity

---

## Decision 002 — Single Canonical Theme

We will NOT create per-org themes.

We will maintain:

themes/gymnastics/

Reason:

- Maintainability
- Version control
- Controlled styling
- Upgrade path

---

## Decision 003 — Firestore as CMS Source

All content stored in:

orgs/{org_id}/site/

Reason:

- Multi-tenant isolation
- Environment safety
- No repo-per-org
- Clean API control

---

## Decision 004 — Structured Data Only

Firestore must NOT store HTML.

Reason:

- Security
- Clean rendering
- Theme independence
- Future portability

---

## Decision 005 — Async Publish Only

Publishing must use Pub/Sub.

No blocking builds allowed.

Reason:

- Align with async-first architecture
- Prevent Cloud Run timeouts
- Enable locking & retry

---

## Decision 006 — No jQuery / Legacy Plugins

Theme must use:

- Tailwind
- Swiper.js
- Vanilla JS

Reason:

- Maintainability
- Performance
- Modern standards
- Avoid plugin fragility

---

## Decision 007 — Environment Isolation Required

Publishing must deploy to active environment only.

No cross-environment contamination allowed.
