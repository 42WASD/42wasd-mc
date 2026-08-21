# Implementation — Progress

This page tracks the build status of every phase in the
[Build (Implementation Phases)](../reference-design/build/03-step-by-step-implementation/index.md)
section of the Reference Design.

> The phase-by-phase **rollout order** is defined in
> [Phase 27 — Rollout order](../reference-design/build/03-step-by-step-implementation/27-44-phase-27-rollout-order/index.md).

## How to update

- Edit `docs/implementation/progress.yaml` to bump a phase's status
  (`done`, `in-progress`, `not-started`, `blocked`, `deferred`).
- Record commands you ran in
  `docs/implementation/_runbook/<part>/phase-<NN>-<slug>.md`.
- Regenerate this page:
  `python3 scripts/docs/docs-generate-implementation.py`
- Rebuild:
  `cd projects && uv run mkdocs build --strict -f ../mkdocs.yml`

<!-- BEGIN_GENERATED_IMPLEMENTATION -->

## Overall progress

**0 / 28** phases/sections complete (**0%**).

<div class="progress-row" style="max-width:720px;padding:8px 0;"><div class="progress-track"><div class="progress-fill progress-fill--shimmer" style="--w:0.0%"></div></div><div class="progress-pct">0%</div></div>

| Status | Count |
|--------|-------|
| ✅ done | 0 |
| 🔶 in-progress | 0 |
| ⬜ not-started | 28 |
| ❌ blocked | 0 |
| ⏸️ deferred | 0 |

## Progress by part

### 0% — Part III — Step-by-step implementation

<div class="tip" style="display:flex;align-items:center;gap:8px;max-width:520px;padding:2px 0 10px;"><div class="progress-track"><div class="progress-fill" style="--w:0.0%"></div></div><div class="progress-pct" style="font-size:.85em;">0%</div><div class="tip-box"><strong>Done (0)</strong>
—
<hr style="opacity:.3;margin:6px 0;"><strong>Pending (28)</strong>
• Phase 0 — Decide names before deploying
• Phase 1 — Create repository structure
• Phase 2 — Create Kubernetes namespaces
• Phase 3 — Deploy CockroachDB and Nakama
• Phase 4 — Deploy Velocity
• Phase 5 — Deploy the Paper lobby
• Phase 6 — Install TAB
• Phase 7 — Add ViaVersion and ViaBackwards
• Phase 8 — Deploy the Forge 1.20.1 fantasy runtime
• Phase 9 — Define the runtime catalog
• Phase 10 — Define map metadata
• Phase 11 — Build the World Controller
• Phase 12 — Build NetworkBridge for Velocity
• Phase 13 — Implement friends and parties
• Phase 14 — Implement `/join <friend>`
• Phase 15 — Implement pending cross-runtime invites
• Phase 16 — Publish Modrinth Server Projects
• Phase 17 — Add packwiz CI
• Phase 18 — Add exact world/dimension TAB information
• Phase 19 — Implement the glitch/random portal
• Phase 20 — Add mc-router
• Phase 21 — Add idle sleep
• Phase 22 — Add Agones only for session worlds
• Phase 23 — Add AI proximity chat
• Phase 24 — Community map upload pipeline
• Phase 25 — Backups
• Phase 26 — Monitoring
• Phase 27 — Rollout order</div></div>

- ⬜ `not-started` — [Phase 0 — Decide names before deploying](../reference-design/build/03-step-by-step-implementation/00-17-phase-0-decide-names-before-deploying/index.md)
- ⬜ `not-started` — [Phase 1 — Create repository structure](../reference-design/build/03-step-by-step-implementation/01-18-phase-1-create-repository-structure/index.md)
- ⬜ `not-started` — [Phase 2 — Create Kubernetes namespaces](../reference-design/build/03-step-by-step-implementation/02-19-phase-2-create-kubernetes-namespaces/index.md)
- ⬜ `not-started` — [Phase 3 — Deploy CockroachDB and Nakama](../reference-design/build/03-step-by-step-implementation/03-20-phase-3-deploy-cockroachdb-and-nakama/index.md)
- ⬜ `not-started` — [Phase 4 — Deploy Velocity](../reference-design/build/03-step-by-step-implementation/04-21-phase-4-deploy-velocity/index.md)
- ⬜ `not-started` — [Phase 5 — Deploy the Paper lobby](../reference-design/build/03-step-by-step-implementation/05-22-phase-5-deploy-the-paper-lobby/index.md)
- ⬜ `not-started` — [Phase 6 — Install TAB](../reference-design/build/03-step-by-step-implementation/06-23-phase-6-install-tab/index.md)
- ⬜ `not-started` — [Phase 7 — Add ViaVersion and ViaBackwards](../reference-design/build/03-step-by-step-implementation/07-24-phase-7-add-viaversion-and-viabackwards/index.md)
- ⬜ `not-started` — [Phase 8 — Deploy the Forge 1.20.1 fantasy runtime](../reference-design/build/03-step-by-step-implementation/08-25-phase-8-deploy-the-forge-1-20-1-fantasy-runtime/index.md)
- ⬜ `not-started` — [Phase 9 — Define the runtime catalog](../reference-design/build/03-step-by-step-implementation/09-26-phase-9-define-the-runtime-catalog/index.md)
- ⬜ `not-started` — [Phase 10 — Define map metadata](../reference-design/build/03-step-by-step-implementation/10-27-phase-10-define-map-metadata/index.md)
- ⬜ `not-started` — [Phase 11 — Build the World Controller](../reference-design/build/03-step-by-step-implementation/11-28-phase-11-build-the-world-controller/index.md)
- ⬜ `not-started` — [Phase 12 — Build NetworkBridge for Velocity](../reference-design/build/03-step-by-step-implementation/12-29-phase-12-build-networkbridge-for-velocity/index.md)
- ⬜ `not-started` — [Phase 13 — Implement friends and parties](../reference-design/build/03-step-by-step-implementation/13-30-phase-13-implement-friends-and-parties/index.md)
- ⬜ `not-started` — [Phase 14 — Implement `/join <friend>`](../reference-design/build/03-step-by-step-implementation/14-31-phase-14-implement-join-friend/index.md)
- ⬜ `not-started` — [Phase 15 — Implement pending cross-runtime invites](../reference-design/build/03-step-by-step-implementation/15-32-phase-15-implement-pending-cross-runtime-invites/index.md)
- ⬜ `not-started` — [Phase 16 — Publish Modrinth Server Projects](../reference-design/build/03-step-by-step-implementation/16-33-phase-16-publish-modrinth-server-projects/index.md)
- ⬜ `not-started` — [Phase 17 — Add packwiz CI](../reference-design/build/03-step-by-step-implementation/17-34-phase-17-add-packwiz-ci/index.md)
- ⬜ `not-started` — [Phase 18 — Add exact world/dimension TAB information](../reference-design/build/03-step-by-step-implementation/18-35-phase-18-add-exact-world-dimension-tab-information/index.md)
- ⬜ `not-started` — [Phase 19 — Implement the glitch/random portal](../reference-design/build/03-step-by-step-implementation/19-36-phase-19-implement-the-glitch-random-portal/index.md)
- ⬜ `not-started` — [Phase 20 — Add mc-router](../reference-design/build/03-step-by-step-implementation/20-37-phase-20-add-mc-router/index.md)
- ⬜ `not-started` — [Phase 21 — Add idle sleep](../reference-design/build/03-step-by-step-implementation/21-38-phase-21-add-idle-sleep/index.md)
- ⬜ `not-started` — [Phase 22 — Add Agones only for session worlds](../reference-design/build/03-step-by-step-implementation/22-39-phase-22-add-agones-only-for-session-worlds/index.md)
- ⬜ `not-started` — [Phase 23 — Add AI proximity chat](../reference-design/build/03-step-by-step-implementation/23-40-phase-23-add-ai-proximity-chat/index.md)
- ⬜ `not-started` — [Phase 24 — Community map upload pipeline](../reference-design/build/03-step-by-step-implementation/24-41-phase-24-community-map-upload-pipeline/index.md)
- ⬜ `not-started` — [Phase 25 — Backups](../reference-design/build/03-step-by-step-implementation/25-42-phase-25-backups/index.md)
- ⬜ `not-started` — [Phase 26 — Monitoring](../reference-design/build/03-step-by-step-implementation/26-43-phase-26-monitoring/index.md)
- ⬜ `not-started` — [Phase 27 — Rollout order](../reference-design/build/03-step-by-step-implementation/27-44-phase-27-rollout-order/index.md)

<!-- END_GENERATED_IMPLEMENTATION -->