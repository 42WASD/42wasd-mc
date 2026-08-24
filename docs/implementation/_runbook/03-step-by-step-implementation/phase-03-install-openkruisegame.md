---
phase: 03-step-by-step-implementation/install-openkruisegame
---

# Runbook — Phase 3: Install OpenKruiseGame

## What was done

Installed the two OpenKruise components the World Controller depends on —
**Kruise** (core controllers) and **Kruise-Game** (GameServer/GameServerSet) —
into `alpha-games-prd`. Installed as `jyao` (cluster admin) via an interactive
`ssh jyao@alpha` session.

- **Helm** was not present on the host, so installed
  `helm` v3.16.4 to `~/bin/helm` (home bin, no sudo needed).
- **Kruise** core `1.9.1` → namespace `kruise-system`, helm release `kruise`.
- **Kruise-Game** `1.1.0` (the pinned OKG version from
  `verified-versions.yaml`) → namespace `kruise-game-system`, helm release
  `kruise-game`.

### Install note (helm + local tgz quirk)

Helm's `--create-namespace` does **not** work when installing from a local
`.tgz` path. The namespace must be created and **owned by Helm** first, or helm
fails with `cannot re-use a name that is still in use` / invalid ownership.
Reliable recipe:

```bash
kubectl create namespace kruise-system
kubectl label namespace kruise-system app.kubernetes.io/managed-by=Helm
kubectl annotate namespace kruise-system \
  meta.helm.sh/release-name=kruise \
  meta.helm.sh/release-namespace=kruise-system
helm install kruise /tmp/kruise.tgz --namespace kruise-system
```

A corrupted failed release was purged by deleting the namespace; the
`kruise-daemon-config` namespace left by the daemon was removed too.

## Commands run

```bash
# On host (jyao@alpha): install helm to home bin
curl -fsSL https://get.helm.sh/helm-v3.16.4-linux-amd64.tar.gz -o /tmp/helm.tgz
tar -xzf /tmp/helm.tgz -C /tmp && mv /tmp/linux-amd64/helm ~/bin/helm

# Download charts (GitHub CDN refused once transiently; retry succeeded)
curl -fsSL -o /tmp/kruise.tgz \
  https://github.com/openkruise/charts/releases/download/kruise-1.9.1/kruise-1.9.1.tgz
curl -fsSL -o /tmp/kruise-game.tgz \
  https://github.com/openkruise/charts/releases/download/kruise-game-1.1.0/kruise-game-1.1.0.tgz

# Kruise core
kubectl create namespace kruise-system
kubectl label namespace kruise-system app.kubernetes.io/managed-by=Helm
kubectl annotate namespace kruise-system \
  meta.helm.sh/release-name=kruise meta.helm.sh/release-namespace=kruise-system
helm install kruise /tmp/kruise.tgz --namespace kruise-system

# Kruise-Game
kubectl create namespace kruise-game-system
kubectl label namespace kruise-game-system app.kubernetes.io/managed-by=Helm
kubectl annotate namespace kruise-game-system \
  meta.helm.sh/release-name=kruise-game meta.helm.sh/release-namespace=kruise-game-system
helm install kruise-game /tmp/kruise-game.tgz --namespace kruise-game-system

# Verify CRDs + smoke test the 0→1 primitive
kubectl api-resources --api-group=game.kruise.io
kubectl apply -f /tmp/gss-smoke.yaml   # GameServerSet replicas: 1
kubectl get gs -n default              # smoke-gss-0 -> Ready
kubectl delete gameserverset smoke-gss -n default
```

## Verified / observed

- Helm releases `kruise` (deployed) and `kruise-game` (deployed).
- Kruise controller-manager 2/2 Ready + daemon Running in `kruise-system`.
- Kruise-Game controller-manager Running in `kruise-game-system`.
- CRDs present: `gameservers.game.kruise.io`, `gameserversets.game.kruise.io`
  (plus full `apps.kruise.io` / `policy.kruise.io` set from Kruise core).
- **Acceptance passed:** scratch `GameServerSet smoke-gss` with `replicas: 1`
  produced `GameServer smoke-gss-0` in `Ready` state with a Running pod
  (readiness gates 2/2), then cleaned up. This is the exact primitive the
  World Controller drives.
- Added `kruise: 1.9.1` and `openkruisegame: 1.1.0` to
  `verified-versions.yaml`.
- Marked phase 3 `done` in `progress.yaml` and regenerated
  `docs/implementation/index.md`.

## Outcome

OKG is installed and its scale primitive is proven. Next: Phase 4 — Install
KEDA and the observability stack.