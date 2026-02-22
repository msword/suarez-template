# Gymnastics Vertical — Risks & Safeguards

## Risk 001 — Environment Misrouting

Publishing to wrong Firebase project.

Mitigation:

- Explicit env config
- ENV assertion at startup
- Deploy target validation

---

## Risk 002 — Concurrent Publish

Two publishes at once.

Mitigation:

- Firestore publish lock document
- TTL enforcement
- 409 response on active lock

---

## Risk 003 — HTML Injection

If HTML allowed in Firestore.

Mitigation:

- Structured data only
- No raw HTML fields

---

## Risk 004 — Theme Drift

Per-org customization leads to fragmentation.

Mitigation:

- Single canonical theme
- Controlled configuration surface

---

## Risk 005 — Future Score Complexity

Scoring system may become highly complex.

Mitigation:

- Separate scoring module
- Do not couple to CMS
- Keep CMS strictly content-focused
