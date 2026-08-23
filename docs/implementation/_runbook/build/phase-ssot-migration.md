---
phase: reference-design/03-step-by-step-implementation/create-repository-structure
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