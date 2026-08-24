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

**1 / 31** phases/sections complete (**3%**).

<div class="progress-row" style="max-width:720px;padding:8px 0;"><div class="progress-track"><div class="progress-fill progress-fill--shimmer" style="--w:3.2%"></div></div><div class="progress-pct">3%</div></div>

| Status | Count |
|--------|-------|
| ✅ done | 1 |
| 🔶 in-progress | 0 |
| ⬜ not-started | 30 |
| ❌ blocked | 0 |
| ⏸️ deferred | 0 |

## Progress by part

### 3% — Part III — Step-by-step implementation

<div class="tip" style="display:flex;align-items:center;gap:8px;max-width:520px;padding:2px 0 10px;"><div class="progress-track"><div class="progress-fill" style="--w:3.0%"></div></div><div class="progress-pct" style="font-size:.85em;">3%</div><div class="tip-box"><strong>Done (1)</strong>
• Decide names before deploying
<hr style="opacity:.3;margin:6px 0;"><strong>Pending (30)</strong>
• Create repository structure
• Create Kubernetes namespaces
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

- ⬜ `not-started` — [Phase 1 — Create repository structure](../reference-design/03-step-by-step-implementation/create-repository-structure/index.md)
- ⬜ `not-started` — [Phase 2 — Create Kubernetes namespaces](../reference-design/03-step-by-step-implementation/create-kubernetes-namespaces/index.md)
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