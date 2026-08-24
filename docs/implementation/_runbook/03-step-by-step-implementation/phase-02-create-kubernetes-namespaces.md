---
phase: 03-step-by-step-implementation/create-kubernetes-namespaces
---

# Runbook — Phase 2: Create Kubernetes namespaces

## What was done

Reconciled the namespace strategy with the tenant-namespace policy that
actually exists on `alpha-games-prd`, rather than creating the reference
design's generic `minecraft` / `minecraft-system` split.

- **Confirmed the live cluster state** (context `alpha-games-prd`):
  `prd-games-42wasd-admin` already exists and is `Active`; its `dev-`
  mirror `dev-games-42wasd-admin` also exists. No `minecraft`,
  `minecraft-system`, `platform`, `proxy`, or `game-backends` namespaces
  exist.
- **Decision: one shared games namespace**, not the two-namespace split.
  Grounded in Kubernetes namespace guidance (namespaces are for
  team/tenant/resource boundaries; prefer labels within a shared namespace
  unless hard isolation is needed) and Argo CD ApplicationSets (host many
  games in one namespace, label-scoped).
- **Documented the "why"** in the Phase-2 reference-design doc:
  env boundary = namespace (`prd-` vs `dev-`); shared platform (Velocity,
  lobby, World Controller, NetworkBridge, CockroachDB, Nakama) must not be
  per-game; game/world boundary = labels + Argo CD `Application`s.
- Kept the declarative source of truth at
  `clusters/alpha/namespace.yaml` (namespace `prd-games-42wasd-admin`,
  labels `environment: prd` + `app.kubernetes.io/managed-by: gitops`).

## Commands run

```bash
# Read-only probes — confirm existing namespaces and context
kubectl config current-context
kubectl get ns

# No mutation: the namespace already exists on the cluster.
# Declarative manifest is the GitOps source of truth; apply only if a
# fresh cluster lacks it:
# kubectl apply -f clusters/alpha/namespace.yaml
```

## Verified / observed

- Context is `alpha-games-prd`.
- `prd-games-42wasd-admin` present (Active) — no `kubectl apply` needed for
  the existing prod namespace.
- All component manifests now target `prd-games-42wasd-admin` (reconciled in
  Phase 1) — grep found no stale `platform`/`proxy`/`game-backends` refs.
- Marked phase 2 `done` in `progress.yaml` and regenerated
  `docs/implementation/index.md`.

## Outcome

Namespace strategy is locked as **single shared games namespace + labels +
per-game Argo CD Applications**. Next: Phase 3 — Install OpenKruiseGame.