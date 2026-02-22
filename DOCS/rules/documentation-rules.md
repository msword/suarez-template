# Gymnastics Module — Documentation Rules

Author: Matthew Sword  
Module: Gymnastics Vertical  
Scope: modules/gymnastics  
Status: Active  
Last Updated: 2026-02-22

---

# Purpose

This document defines mandatory documentation discipline for the Gymnastics module.

The Gymnastics module is treated as a product inside BuzzPoint.

All architecture, contracts, schema, export logic, and publishing rules must be documented.

No undocumented structural changes are permitted.

---

# Core Rule

If the code changes structure, contracts, schema, or flow — documentation must change in the same commit.

Documentation is not optional.
Documentation is not post-work.
Documentation is part of the feature.

---

# Required Documentation Structure

The module must maintain the following:

```
modules/gymnastics/

  feature/
  handoff/
  rules/
  documentation-rules.md
```

Within `rules/`, the following canonical files must exist:

- vertical-gymnastics-overview.md
- vertical-gymnastics-decisions.md
- vertical-gymnastics-schema.md
- vertical-gymnastics-rules.md
- vertical-gymnastics-risks.md
- vertical-gymnastics-publish-flow.md
- site-cms.md

No undocumented feature may be introduced.

---

# Handoff Discipline

All major backend or architectural changes require a handoff document.

Handoff files must:

- Be saved under `/handoff/`
- Include objective
- Include scope
- Include schema impact
- Include export impact
- Include risks
- Include required verification steps

No silent architectural changes.

---

# Feature Documentation Requirements

Each new feature must include:

1. Purpose
2. Problem it solves
3. Data impact
4. Hugo impact
5. Firestore impact
6. Export impact
7. Risk analysis
8. Rollback strategy

If any of the above are missing, the feature is incomplete.

---

# Schema Governance

If any of the following change:

- Firestore collection structure
- Required fields
- Field naming
- Slug rules
- Status rules
- Idempotency rules
- Section naming
- Hugo front matter format

Then:

1. `vertical-gymnastics-schema.md` must be updated.
2. `vertical-gymnastics-rules.md` must be updated if logic changed.
3. Seeder documentation must reflect change.
4. Export documentation must reflect change.

Schema drift is forbidden.

---

# Naming Governance

The following section names are canonical:

- gymnasts
- coaches
- competitions
- meets

Singular versions are forbidden.

Any attempt to introduce:

- athlete
- athletes
- competition (singular)
- coach (singular folder)

Must be rejected unless approved and documented.

---

# Contract Change Rule

If API responses change:

- Response field names
- Status logic
- Pagination logic
- Filtering logic

Then:

1. Module documentation must be updated.
2. Any dependent UI or export logic must be noted.
3. Version impact must be recorded in decisions.md.

No breaking change without documentation.

---

# Publishing Flow Governance

If any change impacts:

- Firestore → Markdown export
- Markdown → Hugo build
- Hugo → Firebase deploy
- Multi-tenant separation
- Static asset mapping
- Slug generation

Then:

`vertical-gymnastics-publish-flow.md` must be updated.

Publishing logic is a critical system.

---

# Risk Governance

When introducing:

- AI scoring
- Image ingestion
- OCR
- Score idempotency logic
- Meet aggregation
- Cross-year historical stats
- Multi-tenant templating

You must update:

`vertical-gymnastics-risks.md`

All scaling risks must be captured.

---

# Versioning Discipline

Every structural decision must be logged in:

`vertical-gymnastics-decisions.md`

Format:

```
Date:
Decision:
Reason:
Impact:
Rollback Plan:
```

No undocumented architectural pivots.

---

# Documentation Format Standards

All module documents must:

- Use clear section headers
- Avoid emotional commentary
- Define rules precisely
- Avoid speculative language
- Separate rules from implementation notes
- Separate architecture from future ideas

Documentation is engineering-grade, not brainstorming.

---

# Verification Requirement

Before merging any feature branch:

Verify:

- Hugo builds clean
- Seeder enforces idempotency
- No duplicate content folders
- No naming drift
- Documentation updated

If documentation not updated → merge blocked.

---

# Module Integrity Standard

The Gymnastics module is designed to:

- Be sellable as an add-on
- Operate independently
- Maintain schema stability
- Maintain deterministic builds
- Support multi-tenant usage

Documentation discipline protects future revenue.

---

# Future Recommendation (Strongly Suggested)

Add:

```
modules/gymnastics/changelog.md
```

Track:

- Version
- Date
- Change
- Impact

Treat this module like a product.

---

End of Document.
