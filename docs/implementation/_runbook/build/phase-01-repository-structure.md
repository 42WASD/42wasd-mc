---
phase: reference-design/build/03-step-by-step-implementation/01-18-phase-1-create-repository-structure
---
# Repository structure replication + infra skeleton

## What was done

Replicated the reference repo (`/home/jyao/ubuntu-server-iac`) structure into
this repo, applied the Minecraft architecture material, and built the `infra/`
IaC skeleton.

## Commands

```bash
# Remove deprecated linear doc dirs
git rm -r docs/00-understand docs/01-implement docs/02-reference \
         docs/03-operations docs/04-resources

# Run generators to rebuild nav + implementation page
uv run --project projects python3 scripts/docs/docs-generate-nav.py
uv run --project projects python3 scripts/docs/docs-generate-implementation.py

# Strict build (repeated while fixing broken links)
pushd projects && uv run mkdocs build --strict -f ../mkdocs.yml
```

## Verified

- `uv run mkdocs build --strict -f ../mkdocs.yml` passes with no warnings.
- Generated nav covers setup/guides/reference-design/implementation.
- `infra/` contains ansible roles, kubernetes manifests, docs, and empty
  `autoinstall/`, `developer/`, `tofu/` dirs.