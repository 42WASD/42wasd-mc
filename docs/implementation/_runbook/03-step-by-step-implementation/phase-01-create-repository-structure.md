---
phase: 03-step-by-step-implementation/create-repository-structure
---

# Runbook — Phase 1: Create repository structure

## What was done

Established the top-level repository structure that matches the reference
design exactly, and migrated the stale in-place Kubernetes manifests into it.

- Created top-level directories: `clusters/`, `runtimes/`, `maps/`,
  `services/`, each with a `README.md` explaining its role.
- Created `clusters/alpha/` (alpha-games-prd) with the component layout
  (`velocity/`, `lobby/`, `nakama/`, `cockroachdb/`, `mc-router/`,
  `monitoring/`) per the Phase 1 reference-design doc.
- Migrated the old `infra/kubernetes/{platform,tenants}` manifests into
  `clusters/alpha/<component>/` and reconciled every namespace reference from
  the stale `platform`/`proxy`/`game-backends` values to the real games
  namespace `prd-games-42wasd-admin`.
- Removed the `infra/` directory entirely (it is not part of the reference
  design's target structure). Its secret/kubeconfig ignore rules were folded
  into the root `.gitignore`; the operator architecture notes were already
  covered by `docs/reference-design/` and `docs/guides/`.
- Updated root `README.md` and `docs/index.md` to describe the new layout.
- Added kustomize bases for each component and an aggregate overlay at
  `clusters/alpha/kustomization.yaml`.

## Commands run

```bash
# Create the top-level structure
mkdir -p clusters/alpha/{velocity,lobby,nakama,cockroachdb,mc-router,monitoring}
mkdir -p runtimes maps services

# Remove the stale infra/ tree (fully migrated + folded ignore rules)
rm -rf infra

# Validate the alpha overlay renders cleanly and targets the right namespace
kubectl kustomize clusters/alpha >/dev/null
kubectl kustomize clusters/alpha | grep -E "kind:|name: prd-games|namespace:"
```

## Verified / observed

- `kubectl kustomize clusters/alpha` builds cleanly.
- All rendered resources target namespace `prd-games-42wasd-admin`.
- No remaining references to the old `platform`/`proxy`/`game-backends`
  namespaces in the migrated manifests.
- Marked phase 1 `done` in `progress.yaml` and regenerated
  `docs/implementation/index.md`.