# Implementation — Progress

This page tracks the build status of every phase in the
[Build (Implementation Phases)](../reference-design/03-step-by-step-implementation/index.md)
section of the Reference Design.

> The phase-by-phase **rollout order** is defined in
> [Phase 30 — Rollout order](../reference-design/03-step-by-step-implementation/rollout-order/index.md).

## How to update

- Edit `docs/implementation/progress.yaml` to bump a phase's status
  (`done`, `in-progress`, `not-started`, `blocked`, `deferred`).
- Regenerate this page:
  `python3 scripts/docs/docs-generate-implementation.py`
- Rebuild:
  `cd projects && uv run mkdocs build --strict -f ../mkdocs.yml`

<!-- BEGIN_GENERATED_IMPLEMENTATION -->

## Overall progress

**3 / 31** phases/sections complete (**10%**).

<div class="progress-row" style="max-width:720px;padding:8px 0;"><div class="progress-track"><div class="progress-fill progress-fill--shimmer" style="--w:9.7%"></div></div><div class="progress-pct">10%</div></div>

| Status | Count |
|--------|-------|
| ✅ done | 3 |
| 🔶 in-progress | 0 |
| ⬜ not-started | 28 |
| ❌ blocked | 0 |
| ⏸️ deferred | 0 |

## Progress by part

### 10% — Part III — Step-by-step implementation

<div class="tip" style="display:flex;align-items:center;gap:8px;max-width:520px;padding:2px 0 10px;"><div class="progress-track"><div class="progress-fill" style="--w:10.0%"></div></div><div class="progress-pct" style="font-size:.85em;">10%</div><div class="tip-box"><strong>Done (3)</strong>
• Decide names before deploying
• Create repository structure
• Create Kubernetes namespaces
<hr style="opacity:.3;margin:6px 0;"><strong>Pending (28)</strong>
• Install OpenKruiseGame
• Install KEDA and the observability stack
• Deploy CockroachDB and Nakama
• Deploy Velocity
• Deploy the Paper lobby
• Install TAB
• Add ViaVersion and ViaBackwards
• Deploy the Forge 1.20.1 fantasy runtime
• Define the runtime catalog
• Define map metadata
• Build the World Controller
• Build NetworkBridge for Velocity
• Implement friends and parties
• Implement `/join <friend>`
• Implement pending cross-runtime invites
• Publish Modrinth Server Projects
• Add packwiz CI
• Add exact world/dimension TAB information
• Implement the glitch/random portal
• Add mc-router
• Add idle sleep
• Add Agones only for session worlds
• Add AI proximity chat
• Add object storage for the community upload pipeline
• Community map upload pipeline
• Backups
• Monitoring
• Rollout order</div></div>

- ✅ `done` — [Phase 0 — Decide names before deploying](../reference-design/03-step-by-step-implementation/decide-names-before-deploying/index.md)

<details markdown="1" class="runbook">
<summary>✅ 📜 Build log — Decide names before deploying</summary>

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

</details>

- ✅ `done` — [Phase 1 — Create repository structure](../reference-design/03-step-by-step-implementation/create-repository-structure/index.md)

<details markdown="1" class="runbook">
<summary>✅ 📜 Build log — Create repository structure</summary>

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

</details>

- ✅ `done` — [Phase 2 — Create Kubernetes namespaces](../reference-design/03-step-by-step-implementation/create-kubernetes-namespaces/index.md)

<details markdown="1" class="runbook">
<summary>✅ 📜 Build log — Create Kubernetes namespaces</summary>

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

</details>

- ⬜ `not-started` — [Phase 3 — Install OpenKruiseGame](../reference-design/03-step-by-step-implementation/install-openkruisegame/index.md)
- ⬜ `not-started` — [Phase 4 — Install KEDA and the observability stack](../reference-design/03-step-by-step-implementation/install-keda-and-observability/index.md)
- ⬜ `not-started` — [Phase 5 — Deploy CockroachDB and Nakama](../reference-design/03-step-by-step-implementation/deploy-cockroachdb-and-nakama/index.md)
- ⬜ `not-started` — [Phase 6 — Deploy Velocity](../reference-design/03-step-by-step-implementation/deploy-velocity/index.md)
- ⬜ `not-started` — [Phase 7 — Deploy the Paper lobby](../reference-design/03-step-by-step-implementation/deploy-the-paper-lobby/index.md)
- ⬜ `not-started` — [Phase 8 — Install TAB](../reference-design/03-step-by-step-implementation/install-tab/index.md)
- ⬜ `not-started` — [Phase 9 — Add ViaVersion and ViaBackwards](../reference-design/03-step-by-step-implementation/add-viaversion-and-viabackwards/index.md)
- ⬜ `not-started` — [Phase 10 — Deploy the Forge 1.20.1 fantasy runtime](../reference-design/03-step-by-step-implementation/deploy-the-forge-1-20-1-fantasy-runtime/index.md)
- ⬜ `not-started` — [Phase 11 — Define the runtime catalog](../reference-design/03-step-by-step-implementation/define-the-runtime-catalog/index.md)
- ⬜ `not-started` — [Phase 12 — Define map metadata](../reference-design/03-step-by-step-implementation/define-map-metadata/index.md)
- ⬜ `not-started` — [Phase 13 — Build the World Controller](../reference-design/03-step-by-step-implementation/build-the-world-controller/index.md)
- ⬜ `not-started` — [Phase 14 — Build NetworkBridge for Velocity](../reference-design/03-step-by-step-implementation/build-networkbridge-for-velocity/index.md)
- ⬜ `not-started` — [Phase 15 — Implement friends and parties](../reference-design/03-step-by-step-implementation/implement-friends-and-parties/index.md)
- ⬜ `not-started` — [Phase 16 — Implement `/join <friend>`](../reference-design/03-step-by-step-implementation/implement-join-friend/index.md)
- ⬜ `not-started` — [Phase 17 — Implement pending cross-runtime invites](../reference-design/03-step-by-step-implementation/implement-pending-cross-runtime-invites/index.md)
- ⬜ `not-started` — [Phase 18 — Publish Modrinth Server Projects](../reference-design/03-step-by-step-implementation/publish-modrinth-server-projects/index.md)
- ⬜ `not-started` — [Phase 19 — Add packwiz CI](../reference-design/03-step-by-step-implementation/add-packwiz-ci/index.md)
- ⬜ `not-started` — [Phase 20 — Add exact world/dimension TAB information](../reference-design/03-step-by-step-implementation/add-exact-world-dimension-tab-information/index.md)
- ⬜ `not-started` — [Phase 21 — Implement the glitch/random portal](../reference-design/03-step-by-step-implementation/implement-the-glitch-random-portal/index.md)
- ⬜ `not-started` — [Phase 22 — Add mc-router](../reference-design/03-step-by-step-implementation/add-mc-router/index.md)
- ⬜ `not-started` — [Phase 23 — Add idle sleep](../reference-design/03-step-by-step-implementation/add-idle-sleep/index.md)
- ⬜ `not-started` — [Phase 24 — Add Agones only for session worlds](../reference-design/03-step-by-step-implementation/add-agones-only-for-session-worlds/index.md)
- ⬜ `not-started` — [Phase 25 — Add AI proximity chat](../reference-design/03-step-by-step-implementation/add-ai-proximity-chat/index.md)
- ⬜ `not-started` — [Phase 26 — Add object storage for the community upload pipeline](../reference-design/03-step-by-step-implementation/add-object-storage/index.md)
- ⬜ `not-started` — [Phase 27 — Community map upload pipeline](../reference-design/03-step-by-step-implementation/community-map-upload-pipeline/index.md)
- ⬜ `not-started` — [Phase 28 — Backups](../reference-design/03-step-by-step-implementation/backups/index.md)
- ⬜ `not-started` — [Phase 29 — Monitoring](../reference-design/03-step-by-step-implementation/monitoring/index.md)
- ⬜ `not-started` — [Phase 30 — Rollout order](../reference-design/03-step-by-step-implementation/rollout-order/index.md)

<!-- END_GENERATED_IMPLEMENTATION -->