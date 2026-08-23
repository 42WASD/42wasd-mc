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

## Verified

- `uv run mkdocs build --strict -f ../mkdocs.yml` passes with no warnings.
- Generated nav covers setup/guides/reference-design/implementation.
- `infra/` now contains only game-layer content: `kubernetes/platform`
  (proxy, lobby), `kubernetes/tenants` (Nakama, CockroachDB), and
  `docs/architecture.md`. Host Ansible/inventory/Argo-bootstrap removed;
  `infra/README.md`, `docs/architecture.md`, and `docs/index.md` point at
  `42WASD/ubuntu-server-iac` as the hosting platform.