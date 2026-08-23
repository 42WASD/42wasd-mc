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

**0 / 29** phases/sections complete (**0%**).

<div class="progress-row" style="max-width:720px;padding:8px 0;"><div class="progress-track"><div class="progress-fill progress-fill--shimmer" style="--w:0.0%"></div></div><div class="progress-pct">0%</div></div>

| Status | Count |
|--------|-------|
| ✅ done | 0 |
| 🔶 in-progress | 0 |
| ⬜ not-started | 29 |
| ❌ blocked | 0 |
| ⏸️ deferred | 0 |

## Progress by part

### 0% — Part III — Step-by-step implementation

<div class="tip" style="display:flex;align-items:center;gap:8px;max-width:520px;padding:2px 0 10px;"><div class="progress-track"><div class="progress-fill" style="--w:0.0%"></div></div><div class="progress-pct" style="font-size:.85em;">0%</div><div class="tip-box"><strong>Done (0)</strong>
—
<hr style="opacity:.3;margin:6px 0;"><strong>Pending (29)</strong>
• Decide names before deploying
• Create repository structure
• Create Kubernetes namespaces
• Install OpenKruiseGame
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

# Repository structure replication + infra skeleton

## What was done

Replicated the reference repo (`/home/jyao/ubuntu-server-iac`) structure into
this repo, applied the Minecraft architecture material, and built the `infra/`
IaC skeleton.

### Ownership seam (later cleanup)

`42wasd-mc` targets the same `alpha`/RKE2 platform as
`42WASD/ubuntu-server-iac`. To avoid two source-of-truth IaC stacks, the
duplicate **host/platform** IaC was removed from this repo, leaving only the
Minecraft **game-layer** workloads. The host platform (Ansible, inventory,
RKE2, Argo CD bootstrap, autoinstall, tofu, host runbooks) is owned by
`ubuntu-server-iac`; this repo points at it.

## Commands

```bash
# Remove deprecated linear doc dirs
git rm -r docs/00-understand docs/01-implement docs/02-reference \
         docs/03-operations docs/04-resources

# Remove duplicated host/platform IaC (owned by 42WASD/ubuntu-server-iac)
git rm -r infra/ansible infra/inventory infra/autoinstall \
          infra/developer infra/tofu infra/kubernetes/bootstrap \
          infra/docs/disaster-recovery.md infra/docs/upgrade-runbook.md \
          infra/Makefile

# Run generators to rebuild nav + implementation page
uv run --project projects python3 scripts/docs/docs-generate-nav.py
uv run --project projects python3 scripts/docs/docs-generate-implementation.py

# Strict build (repeated while fixing broken links)
pushd projects && uv run mkdocs build --strict -f ../mkdocs.yml
```

### Documentation: OpenKruiseGame (OKG) adoption

Replaced the hand-rolled `StatefulSet + PVC` persistent-world primitive with an
**OpenKruiseGame `GameServerSet + PVC`** workload across the live
reference-design pages (`docs/reference-design/`), per the 2026-08 online audit
(Shulker dormant at v0.13.0 / 2025-04-05; OKG actively maintained,
CNCF-incubated). The pages are manually maintained (the splitter
`docs/docs-split-minecraft.py` is a one-time scaffold and is NOT wired to the
committed tree), so edits were applied directly to the pages.

```bash
# Full verification pipeline (validate -> tests -> strict build)
bash scripts/docs/verify.sh
# => VERIFY OK
```

## Verified

- `uv run mkdocs build --strict -f ../mkdocs.yml` passes with no warnings.
- Generated nav covers setup/guides/reference-design/implementation.
- `infra/` now contains only game-layer content: `kubernetes/platform`
  (proxy, lobby), `kubernetes/tenants` (Nakama, CockroachDB), and
  `docs/architecture.md`. Host Ansible/inventory/Argo-bootstrap removed;
  `infra/README.md`, `docs/architecture.md`, and `docs/index.md` point at
  `42WASD/ubuntu-server-iac` as the hosting platform.

---

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
- ⬜ `not-started` — [Phase 3 — Install OpenKruiseGame](../reference-design/03-step-by-step-implementation/install-openkruisegame/index.md)

<details markdown="1" class="runbook">
<summary>⬜ 📜 Build log — Install OpenKruiseGame</summary>

# Install OpenKruiseGame (new Phase 3)

## What was done

Created the `install-openkruisegame` phase (new Phase 3, inserted after
`create-kubernetes-namespaces`) so the World Controller's `GameServerSet`
driving is grounded in an actual platform install step. Verified the install
mechanics against the current OpenKruiseGame docs:

- OKG requires **both** Kruise and Kruise-Game, Kubernetes >= 1.18.
- `helm repo add openkruise` → `helm install kruise openkruise/kruise` →
  `helm install kruise-game openkruise/kruise-game`.
- Installs the `game.kruise.io/v1alpha1` API group (GameServerSet, GameServer).
- Also added to this phase: an OKG→World Controller ownership note (World
  Controller scales the GameServerSet via narrow RBAC; it does not install OKG).

## Effects on numbering

Inserting this phase after `create-kubernetes-namespaces` shifted all later
phases +1. Regenerated nav + implementation page; updated the hand-written
prose "Phase N" references:

- `social-state...`: "Phase 5" (Paper lobby) → "Phase 6"
- `current-verification-notes-2026-08-19`: "Phase 5" → "Phase 6"
- `rollout-order`: "Phases 0–27" → "0–28"; CockroachDB "Phase 3" → "4";
  runtime catalog "9 → 10"; map metadata "10 → 11"; added item→phase mapping
  table.
- `docs/implementation/progress.yaml`: inserted Phase 3 comment + renumbered.

## Commands

```bash
# Add the new phase folder + page, then register it in the manifest
# (edits to _sequence.yaml, install-openkruisegame/index.md)

# Regenerate nav + implementation page (must match committed output)
cd /home/jyao/42wasd-mc
python3 scripts/docs/docs-generate-nav.py
python3 scripts/docs/docs-generate-implementation.py

# Full verification pipeline
bash scripts/docs/verify.sh
```

## Result

`bash scripts/docs/verify.sh` → **VERIFY OK** (Layer 1+2 VALIDATION OK, 7
pytest passed, strict mkdocs build succeeded). Generated files were staged so
the golden test compared against the regenerated output.

## Related doc edits (same review pass)

- `social-state...` §7.1.0: corrected the offline/cracked auth model to an
  **in-game auth gate** — player joins, lands on a login stage, completes
  Discord/Google OAuth there, is linked to a Nakama account, then routed on.
- `deploy-cockroachdb-and-nakama`: aligned the flow diagram to the gate model.
- `add-exact-world-dimension-tab-information`: added the missing **backend-side
  presence bridge** description (a per-runtime plugin/mod that reports
  dimension changes keyed by UUID to NetworkBridge/Nakama) — closing the gap
  where exact dimension data never reached TAB.
- `plain-english-glossary`: added "Auth gate".

</details>

- ⬜ `not-started` — [Phase 4 — Deploy CockroachDB and Nakama](../reference-design/03-step-by-step-implementation/deploy-cockroachdb-and-nakama/index.md)
- ⬜ `not-started` — [Phase 5 — Deploy Velocity](../reference-design/03-step-by-step-implementation/deploy-velocity/index.md)
- ⬜ `not-started` — [Phase 6 — Deploy the Paper lobby](../reference-design/03-step-by-step-implementation/deploy-the-paper-lobby/index.md)
- ⬜ `not-started` — [Phase 7 — Install TAB](../reference-design/03-step-by-step-implementation/install-tab/index.md)
- ⬜ `not-started` — [Phase 8 — Add ViaVersion and ViaBackwards](../reference-design/03-step-by-step-implementation/add-viaversion-and-viabackwards/index.md)
- ⬜ `not-started` — [Phase 9 — Deploy the Forge 1.20.1 fantasy runtime](../reference-design/03-step-by-step-implementation/deploy-the-forge-1-20-1-fantasy-runtime/index.md)
- ⬜ `not-started` — [Phase 10 — Define the runtime catalog](../reference-design/03-step-by-step-implementation/define-the-runtime-catalog/index.md)
- ⬜ `not-started` — [Phase 11 — Define map metadata](../reference-design/03-step-by-step-implementation/define-map-metadata/index.md)
- ⬜ `not-started` — [Phase 12 — Build the World Controller](../reference-design/03-step-by-step-implementation/build-the-world-controller/index.md)

<details markdown="1" class="runbook">
<summary>⬜ 📜 Build log — Build the World Controller</summary>

# Maintained-tool fills for the World Controller operator

## What was done

Following a 2026-08 online audit of the operator landscape, added three
actively-maintained tools to the reference design to reduce the custom
World Controller/NetworkBridge code. Each maps to a specific custom piece the
design was hand-rolling:

- **itzg/mc-monitor** → the Minecraft `status/ping` readiness probe and the
  per-server metrics (online, latency, MOTD) exported to Prometheus. Verified
  active: Docker Hub updated within days; v0.17.1 current.
- **KEDA** → the idle/player-count scale-to-zero **trigger** (`ScaledObject` →
  HPA on the GameServerSet). CNCF-graduated. The safe-to-stop decision
  (reservations, draining, maintenance) intentionally stays custom in the
  World Controller.
- **Velero** → the PVC snapshot/restore/schedule + off-machine copy + restore
  test half of the backup pipeline. Apache-2.0, CNCF-governed.

Also confirmed **Argo CD is already owned** by `42WASD/ubuntu-server-iac` (the
host platform), so no GitOps applier was added here. AutoModpack and Gate were
already evaluated and rejected with documented reasons in the reference design.

## Commands

```bash
# Edit target pages (all under docs/reference-design/)
#   04/.../world-readiness-contract          -> mc-monitor (readiness contract)
#   03/.../build-the-world-controller        -> mc-monitor (two-stage readiness)
#   03/.../monitoring                        -> mc-monitor (shared metrics source)
#   03/.../add-idle-sleep                    -> KEDA (scale trigger)
#   03/.../add-mc-router                      -> KEDA (optional edge-wake trigger)
#   03/.../backups                           -> Velero (backup operator)
#   01/.../the-selected-tool-stack           -> added 3 rows
#   02/.../capability-cheat-sheet            -> added 3 rows

# Regenerate nav + implementation index from SSOT (cwd is projects/)
python3 /home/jyao/42wasd-mc/scripts/docs/docs-generate-nav.py
python3 /home/jyao/42wasd-mc/scripts/docs/docs-generate-implementation.py

# Full verification pipeline (validate -> tests -> strict build)
bash /home/jyao/42wasd-mc/scripts/docs/verify.sh
# => VERIFY OK
```

## Verified

- `verify.sh` reports `VERIFY OK` (validate -> 7 pytest -> strict mkdocs build).
- Generated nav and implementation index regenerated cleanly.
- No new phases added to `_sequence.yaml`; the additions strengthen existing
  sections (build-the-world-controller, add-idle-sleep, add-mc-router,
  backups, monitoring, world-readiness-contract).

---

</details>

- ⬜ `not-started` — [Phase 13 — Build NetworkBridge for Velocity](../reference-design/03-step-by-step-implementation/build-networkbridge-for-velocity/index.md)
- ⬜ `not-started` — [Phase 14 — Implement friends and parties](../reference-design/03-step-by-step-implementation/implement-friends-and-parties/index.md)
- ⬜ `not-started` — [Phase 15 — Implement `/join <friend>`](../reference-design/03-step-by-step-implementation/implement-join-friend/index.md)
- ⬜ `not-started` — [Phase 16 — Implement pending cross-runtime invites](../reference-design/03-step-by-step-implementation/implement-pending-cross-runtime-invites/index.md)
- ⬜ `not-started` — [Phase 17 — Publish Modrinth Server Projects](../reference-design/03-step-by-step-implementation/publish-modrinth-server-projects/index.md)
- ⬜ `not-started` — [Phase 18 — Add packwiz CI](../reference-design/03-step-by-step-implementation/add-packwiz-ci/index.md)
- ⬜ `not-started` — [Phase 19 — Add exact world/dimension TAB information](../reference-design/03-step-by-step-implementation/add-exact-world-dimension-tab-information/index.md)
- ⬜ `not-started` — [Phase 20 — Implement the glitch/random portal](../reference-design/03-step-by-step-implementation/implement-the-glitch-random-portal/index.md)
- ⬜ `not-started` — [Phase 21 — Add mc-router](../reference-design/03-step-by-step-implementation/add-mc-router/index.md)
- ⬜ `not-started` — [Phase 22 — Add idle sleep](../reference-design/03-step-by-step-implementation/add-idle-sleep/index.md)
- ⬜ `not-started` — [Phase 23 — Add Agones only for session worlds](../reference-design/03-step-by-step-implementation/add-agones-only-for-session-worlds/index.md)
- ⬜ `not-started` — [Phase 24 — Add AI proximity chat](../reference-design/03-step-by-step-implementation/add-ai-proximity-chat/index.md)
- ⬜ `not-started` — [Phase 25 — Community map upload pipeline](../reference-design/03-step-by-step-implementation/community-map-upload-pipeline/index.md)
- ⬜ `not-started` — [Phase 26 — Backups](../reference-design/03-step-by-step-implementation/backups/index.md)
- ⬜ `not-started` — [Phase 27 — Monitoring](../reference-design/03-step-by-step-implementation/monitoring/index.md)
- ⬜ `not-started` — [Phase 28 — Rollout order](../reference-design/03-step-by-step-implementation/rollout-order/index.md)

<!-- END_GENERATED_IMPLEMENTATION -->