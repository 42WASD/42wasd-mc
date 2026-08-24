# 42wasd-mc

Minecraft network infrastructure, deployed to the `alpha-games-prd` RKE2
cluster. This repository is the single source of truth for the platform —
Git says what **should** exist, Kubernetes says what **is** running.

## Layout

```text
clusters/    # Kubernetes manifests, one dir per environment cluster
runtimes/    # reusable server bytecode stacks (image + side)
maps/        # world data definitions & logical IDs
services/    # custom platform services (world-controller, network-bridge)
docs/        # reference design & implementation runbooks
infra/       # IaC for the underlying hosts (see infra/README.md)
```

## Structure decision (Phase 1)

Top-level directories match the reference design exactly. Kubernetes
manifests that previously lived under `infra/kubernetes/{platform,tenants}`
were migrated into `clusters/alpha/` and reconciled to the real games
namespace (`prd-games-42wasd-admin`). See the Phase 1 runbook.
