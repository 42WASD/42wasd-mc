# Scripts

Utility scripts for the `42wasd-mc` project. Add operational scripts here (mirroring the source repo's layout, which groups them by area under `scripts/`).

## Layout

- `docs/docs-split-minecraft.py` — splits the Minecraft architecture source doc into the `docs/reference-design/` tree.
- `docs/docs-generate-nav.py` — regenerates the nav in `mkdocs.yml`.
- `docs/docs-generate-implementation.py` — regenerates `docs/implementation/index.md` from the runbook.

## Usage

Scripts are run with the `uv` environment when they depend on Python:
```bash
uv run scripts/your-script.py
```
Shell scripts can be run directly:
```bash
bash scripts/your-script.sh
```