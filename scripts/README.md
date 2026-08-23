# Scripts

Utility scripts for the `42wasd-mc` project. Add operational scripts here (mirroring the source repo's layout, which groups them by area under `scripts/`).

## Layout

- `docs/docs_manifest.py` — shared loader for the SSOT reading-order manifest
  (`docs/reference-design/_sequence.yaml`); derives part numerals + phase numbers.
- `docs/docs-generate-nav.py` — regenerates the nav in `mkdocs.yml` from the
  reading-order manifest (SSOT).
- `docs/docs-generate-implementation.py` — regenerates
  `docs/implementation/index.md` from the manifest + `progress.yaml`.
- `docs/docs-split-minecraft.py` — one-time scaffold that split the Minecraft
  architecture source doc into the `docs/reference-design/` tree.

### One-time migration scripts (SSOT)

- `docs/docs-flatten-sequence.py` — flattens `reference-design/` and renames
  sections to bare slugs (`git mv`).
- `docs/docs-strip-sequence-from-pages.py` — strips `Part N —`/`Phase N —`
  prefixes from H1s.
- `docs/docs-migrate-paths.py` — rewrites cross-references to the new flat paths.

## Usage

Scripts are run with the `uv` environment when they depend on Python:
```bash
uv run scripts/your-script.py
```
Shell scripts can be run directly:
```bash
bash scripts/your-script.sh
```