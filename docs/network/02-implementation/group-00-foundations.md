# Group 00 — Foundations

These phases establish stable identifiers, the Git repository layout, and Kubernetes namespaces before any services are deployed.

- **[Phase 0 — Decide names before deploying](phase-00-names.md)** — stable identifiers, no display names as primary keys.
- **[Phase 1 — Create repository structure](phase-01-repo-structure.md)** — Git says what should exist.
- **[Phase 2 — Create Kubernetes namespaces](phase-02-namespaces.md)** — the `minecraft` and `minecraft-system` split.

**Gate:** none. This group has no runtime components; it sets conventions used by everything after.

> **Rollout mapping:** this group is the prerequisite for the rest of the implementation. None of the rollout-order steps 1–19 can start without it.