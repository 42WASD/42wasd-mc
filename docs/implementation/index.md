# Implementation — Progress

This page tracks the build status of every phase in the
[Build (Implementation Phases)](../reference-design/03-step-by-step-implementation/index.md)
section of the Reference Design.

> The phase-by-phase **rollout order** is defined in
> [Phase 27 — Rollout order](../reference-design/03-step-by-step-implementation/rollout-order/index.md).

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
• Decide names before deploying
• Create repository structure
• Create Kubernetes namespaces
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
• Community map upload pipeline
• Backups
• Monitoring
• Rollout order</div></div>

- ⬜ `not-started` — [Phase 0 — Decide names before deploying](../reference-design/03-step-by-step-implementation/decide-names-before-deploying/index.md)
- ⬜ `not-started` — [Phase 1 — Create repository structure](../reference-design/03-step-by-step-implementation/create-repository-structure/index.md)

<details markdown="1" class="runbook">
<summary>⬜ 📜 Build log — Create repository structure</summary>

# SSOT reading-order manifest migration

## What was done

Migrated the reference-design to a Single-Source-of-Truth (SSOT) reading-order
manifest, porting the technique from `42WASD/ubuntu-server-iac`. All hardcoded
numbering (embedded in folder names and H1s) was replaced with numbers derived
from the manifest.

### Files created
- `docs/reference-design/_sequence.yaml` — the SSOT manifest: ordered `parts:`
  list with `tracked:` flags and section slugs.
- `scripts/docs/docs_manifest.py` — shared loader: `load_sequence()`,
  `assign_phase_numbers()`, `phase_by_slug()`; derives Roman numerals and global
  phase numbers from manifest position.
- `scripts/docs/docs-flatten-sequence.py` — one-time flatten + bare-slug rename
  (`git mv`).
- `scripts/docs/docs-strip-sequence-from-pages.py` — one-time H1 prefix strip.
- `scripts/docs/docs-migrate-paths.py` — one-time cross-link rewrite.

### Generators rewritten (now manifest-driven)
- `scripts/docs/docs-generate-nav.py` — derives `Part N — <title>` and
  `Phase N — <title>` nav labels from the manifest (keeps 42wasd-mc Guides nav).
- `scripts/docs/docs-generate-implementation.py` — reads only `tracked: true`
  parts from the manifest; derives links as
  `../reference-design/<part>/<section>/index.md`.

### Structure migration
Flattened `docs/reference-design/` from the 3-group layout
(`background/build/reference`) into a flat parts list, and renamed all section
folders to bare slugs:

- `background/01-understand-...`  -> `01-understand-the-architecture-before-...`
- `background/02-how-to-interpret-...` -> `02-how-to-interpret-the-actual-tools`
- `build/03-step-by-step-implementation/00-17-phase-0-decide-names-...`
  -> `03-step-by-step-implementation/decide-names-before-deploying`
- `reference/04-technical-reference/00-45-recommended-...`
  -> `04-technical-reference/recommended-source-of-truth-model`
- `reference/05-current-verification-references/00-57-final-...`
  -> `05-current-verification-references/final-architecture-recommendation`

Stripped `Part N —` / `Phase N —` prefixes from all H1s (33 files). Updated all
cross-references, `progress.yaml` keys, and the runbook `phase:` frontmatter.

## Commands

```bash
# Flatten + rename sections to bare slugs (git mv)
python3 scripts/docs/docs-flatten-sequence.py

# Strip Part/Phase prefixes from H1s
python3 scripts/docs/docs-strip-sequence-from-pages.py

# Rewrite cross-links to new flat paths
python3 scripts/docs/docs-migrate-paths.py

# Regenerate nav + implementation from the manifest
cd projects
uv run python3 ../scripts/docs/docs-generate-nav.py
uv run python3 ../scripts/docs/docs-generate-implementation.py

# Strict build (repeated while fixing broken links)
uv run mkdocs build --strict -f ../mkdocs.yml
```

## Verified

- `uv run mkdocs build --strict -f ../mkdocs.yml` passes with no warnings
  (only the unrelated MkDocs 2.0 notice).
- Nav shows `I — <part>`, `II — <part>`, ..., and `Phase N — <title>` for the
  tracked build part (Part III), all derived from `_sequence.yaml`.
- Implementation page shows Part III — Step-by-step implementation with 28
  derived phases.
- All 64 `reference-design/**/index.md` files on disk match manifest slugs.

</details>

- ⬜ `not-started` — [Phase 2 — Create Kubernetes namespaces](../reference-design/03-step-by-step-implementation/create-kubernetes-namespaces/index.md)
- ⬜ `not-started` — [Phase 3 — Deploy CockroachDB and Nakama](../reference-design/03-step-by-step-implementation/deploy-cockroachdb-and-nakama/index.md)
- ⬜ `not-started` — [Phase 4 — Deploy Velocity](../reference-design/03-step-by-step-implementation/deploy-velocity/index.md)
- ⬜ `not-started` — [Phase 5 — Deploy the Paper lobby](../reference-design/03-step-by-step-implementation/deploy-the-paper-lobby/index.md)
- ⬜ `not-started` — [Phase 6 — Install TAB](../reference-design/03-step-by-step-implementation/install-tab/index.md)
- ⬜ `not-started` — [Phase 7 — Add ViaVersion and ViaBackwards](../reference-design/03-step-by-step-implementation/add-viaversion-and-viabackwards/index.md)
- ⬜ `not-started` — [Phase 8 — Deploy the Forge 1.20.1 fantasy runtime](../reference-design/03-step-by-step-implementation/deploy-the-forge-1-20-1-fantasy-runtime/index.md)
- ⬜ `not-started` — [Phase 9 — Define the runtime catalog](../reference-design/03-step-by-step-implementation/define-the-runtime-catalog/index.md)
- ⬜ `not-started` — [Phase 10 — Define map metadata](../reference-design/03-step-by-step-implementation/define-map-metadata/index.md)
- ⬜ `not-started` — [Phase 11 — Build the World Controller](../reference-design/03-step-by-step-implementation/build-the-world-controller/index.md)
- ⬜ `not-started` — [Phase 12 — Build NetworkBridge for Velocity](../reference-design/03-step-by-step-implementation/build-networkbridge-for-velocity/index.md)
- ⬜ `not-started` — [Phase 13 — Implement friends and parties](../reference-design/03-step-by-step-implementation/implement-friends-and-parties/index.md)
- ⬜ `not-started` — [Phase 14 — Implement `/join <friend>`](../reference-design/03-step-by-step-implementation/implement-join-friend/index.md)
- ⬜ `not-started` — [Phase 15 — Implement pending cross-runtime invites](../reference-design/03-step-by-step-implementation/implement-pending-cross-runtime-invites/index.md)
- ⬜ `not-started` — [Phase 16 — Publish Modrinth Server Projects](../reference-design/03-step-by-step-implementation/publish-modrinth-server-projects/index.md)
- ⬜ `not-started` — [Phase 17 — Add packwiz CI](../reference-design/03-step-by-step-implementation/add-packwiz-ci/index.md)
- ⬜ `not-started` — [Phase 18 — Add exact world/dimension TAB information](../reference-design/03-step-by-step-implementation/add-exact-world-dimension-tab-information/index.md)
- ⬜ `not-started` — [Phase 19 — Implement the glitch/random portal](../reference-design/03-step-by-step-implementation/implement-the-glitch-random-portal/index.md)
- ⬜ `not-started` — [Phase 20 — Add mc-router](../reference-design/03-step-by-step-implementation/add-mc-router/index.md)
- ⬜ `not-started` — [Phase 21 — Add idle sleep](../reference-design/03-step-by-step-implementation/add-idle-sleep/index.md)
- ⬜ `not-started` — [Phase 22 — Add Agones only for session worlds](../reference-design/03-step-by-step-implementation/add-agones-only-for-session-worlds/index.md)
- ⬜ `not-started` — [Phase 23 — Add AI proximity chat](../reference-design/03-step-by-step-implementation/add-ai-proximity-chat/index.md)
- ⬜ `not-started` — [Phase 24 — Community map upload pipeline](../reference-design/03-step-by-step-implementation/community-map-upload-pipeline/index.md)
- ⬜ `not-started` — [Phase 25 — Backups](../reference-design/03-step-by-step-implementation/backups/index.md)
- ⬜ `not-started` — [Phase 26 — Monitoring](../reference-design/03-step-by-step-implementation/monitoring/index.md)
- ⬜ `not-started` — [Phase 27 — Rollout order](../reference-design/03-step-by-step-implementation/rollout-order/index.md)

<!-- END_GENERATED_IMPLEMENTATION -->