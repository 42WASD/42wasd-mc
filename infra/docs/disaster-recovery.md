# Disaster Recovery

## Recovery objectives

- **RPO** — acceptable data loss window (default: 15 min for worlds).
- **RTO** — acceptable downtime (default: 1 h).

## Critical data

| Data | Where | Back up to |
|------|-------|------------|
| World data | Lobby + world PVCs | S3-compatible bucket |
| Nakama accounts | CockroachDB | SQL dumps |
| Argo CD apps | Git (declarative) | auto (Git) |
| Host state | Ansible (declarative) | auto (Git) |

## Restore sequence

1. Re-provision hosts from `ansible/` (idempotent `make bootstrap`).
2. Reinstall RKE2 (control plane + agents).
3. Reinstall Argo CD (`kubernetes/bootstrap/argocd`).
4. Recreate stateful workloads and restore PVCs / DB dumps.

> **TODO**: add concrete backup scripts + restore runbooks under `tofu/`,
> `developer/`, or `kubernetes/` as phases complete.