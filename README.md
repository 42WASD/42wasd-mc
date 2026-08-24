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
```

The host platform (RKE2 cluster, hosts, GitOps via Argo CD, host-level IaC) is
owned by [`42WASD/ubuntu-server-iac`](https://github.com/42WASD/ubuntu-server-iac);
this repo carries only the Minecraft **game-layer** workloads.

## Structure decision (Phase 1)

Top-level directories match the reference design exactly. Kubernetes
manifests that previously lived under `infra/kubernetes/{platform,tenants}`
were migrated into `clusters/alpha/` and reconciled to the real games
namespace (`prd-games-42wasd-admin`). The former `infra/` directory was then
removed. See the Phase 1 runbook.
