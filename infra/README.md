# infra

Minecraft **game-layer** infrastructure that runs on the 42wasd-mc Kubernetes
network.

> **Hosting platform:** the RKE2 cluster, hosts (`alpha`, `build01`), GitOps
> (Argo CD), and host-level IaC are owned by
> [`42WASD/ubuntu-server-iac`](https://github.com/42WASD/ubuntu-server-iac).
> This repo carries only the **game-layer** manifests that run on that platform,
> and they live in `clusters/` at the repo root (moved from here in Phase 1).

## Layout

- `../clusters/alpha` — game workloads for the alpha cluster (proxy, lobby,
  Nakama, CockroachDB). These moved top-level during Phase 1.
- `docs/` — operator-facing architecture for the game layer.

## Ownership seam

- The **host platform** (Ansible, RKE2, Argo CD bootstrap, storage, monitoring,
  OpenTofu, Ubuntu autoinstall) lives in `42WASD/ubuntu-server-iac`.
- This repo owns only what is **Minecraft-specific**: the proxy/lobby
  workloads and the Nakama/CockroachDB game backends, now under
  `clusters/alpha/`.
- Argo CD is bootstrapped by the platform repo; its `Applications` point at the
  game manifests here via the cluster.

See `docs/architecture.md` for the game-layer operator detail.