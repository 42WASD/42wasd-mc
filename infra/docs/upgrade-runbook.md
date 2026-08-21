# Upgrade Runbook

Sequencing rule: **control plane first, then agents, then apps.** Always back up
state before in-place upgrades.

## 1. RKE2 / Kubernetes

1. `git pull` + review `ansible/roles/rke2_server/defaults/main.yml` version.
2. Upgrade the server: `make ansible` (targets `rke2_servers`).
3. Wait for API to settle; `kubectl get nodes`.
4. Upgrade agents: `make ansible` (targets `rke2_agents`).
5. Drain + uncordon nodes as needed.

## 2. Applications (Argo CD)

1. Commit manifest changes to `infra/kubernetes/`.
2. Argo CD auto-syncs (prune + self-heal).
3. Watch sync status via `argocd app list`.

## 3. Game servers

- Lobby / world images bump via manifest tag change in `kubernetes/`.
- Velocity proxy config via ConfigMap; rolling restart.

> **TODO**: expand with pinned version table + rollback procedures.