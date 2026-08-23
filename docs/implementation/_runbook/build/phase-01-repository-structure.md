---
phase: 03-step-by-step-implementation/create-repository-structure
---
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
