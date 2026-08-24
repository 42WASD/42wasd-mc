---
phase: 03-step-by-step-implementation/decide-names-before-deploying
---

# Runbook — Phase 0: Decide names before deploying

## What was done

Locked the stable identifiers for the deployment, per
`docs/reference-design/03-step-by-step-implementation/decide-names-before-deploying/index.md`.

- Confirmed the cluster/context and namespace from the live cluster:
  - Context: `alpha-games-prd`
  - Namespace: `prd-games-42wasd-admin` (dev mirror: `dev-games-42wasd-admin`)
- Confirmed the public hostname: `minecraft.42base.com` (Cloudflare).
- Defined the world logical ID scheme: `<map-slug>-<uuid8>` (8-hex UUID
  prefix) to guarantee non-collision without a registry/counter.
- Updated the phase-0 reference-design doc with the recorded identifiers.

## Commands run

```bash
# Verify context and namespaces (read-only probes)
kubectl config current-context
kubectl config view --minify -o jsonpath='{.contexts[0].context.namespace}'
kubectl get ns

# No cluster mutations performed in this phase.
```

## Verified / observed

- Namespaces `prd-games-42wasd-admin` and `dev-games-42wasd-admin` exist on
  the cluster; no `platform`/`proxy`/`game-backends` namespaces exist (those
  live only in stale `infra/` manifests).
- Context namespace resolves to `prd-games-42wasd-admin`.
- Marked phase 0 `done` in `progress.yaml` and regenerated
  `docs/implementation/index.md`.
- **Fixed a generator bug** in `scripts/docs/docs-generate-implementation.py`:
  `load_progress()` returned the nested `progress.yaml` dict, but `status_of()`
  looks status up by flat slash-paths, so statuses were never read (all phases
  always showed `not-started`). Added `_flatten()` to collapse nested status
  keys into slash-paths. After the fix, phase 0 correctly shows `✅ done`
  (1/31).
- Ignored large world data in `.gitignore` (`world-data/`, `world-data-export-*.tar.gz`).

## Outcome

Phase 0 is a documentation-only decision phase. Next: Phase 1 — Create
repository structure, then Phase 2 — create the namespaces (aligning the
`infra/` manifests to the actual `prd-games-42wasd-admin` namespace).