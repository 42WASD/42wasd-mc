---
phase: 03-step-by-step-implementation/install-keda-and-observability
---

# Runbook — Phase 4: Install KEDA and the observability stack

## What was done

Installed the two platform pieces later phases assume are present but no step
actually installs: **KEDA** (the event-driven autoscaler driving the
`GameServerSet` 0↔1 transition) and the **Prometheus/Grafana** stack (the
destination for `mc-monitor` metrics and the alerting home). Installed as
`jyao` on `alpha-games-prd`.

- **KEDA** `2.20.2` → namespace `keda`, helm release `keda`. Operator +
  metrics-apiserver + admission-webhooks all `1/1`. CRDs present incl.
  `scaledobjects.keda.sh`.
- **kube-prometheus-stack** `88.5.4` (Prometheus v3.14.0 + Grafana +
  Alertmanager) → namespace `monitoring`, helm release `prometheus`. All pods
  Running (Alertmanager 2/2, Grafana 3/3, Prometheus 2/2, operator,
  kube-state-metrics, node-exporter).
- **ServiceMonitor** `minecraft-servers` created in the games namespace
  (`prd-games-42wasd-admin`) so Prometheus scrapes `mc-monitor` metrics on the
  `metrics` port. Labels match the kube-prometheus-stack
  `serviceMonitorSelector` (`release: prometheus`).
- Noted the **replica-owner rule**: KEDA must only autoscale *pooled* fleets it
  owns; a named persistent world's `GameServerSet` is owned by the World
  Controller and must **not** get a `ScaledObject`. This phase installs no
  ScaledObject.

## Commands run

```bash
# On host (jyao@alpha) — helm in ~/bin
export PATH=$HOME/bin:$PATH

# KEDA
kubectl create namespace keda
kubectl label namespace keda app.kubernetes.io/managed-by=Helm
kubectl annotate namespace keda \
  meta.helm.sh/release-name=keda meta.helm.sh/release-namespace=keda
helm install keda kedacore/keda --version 2.20.2 --namespace keda

# Prometheus + Grafana (kube-prometheus-stack)
kubectl label namespace monitoring app.kubernetes.io/managed-by=Helm
kubectl annotate namespace monitoring \
  meta.helm.sh/release-name=prometheus meta.helm.sh/release-namespace=monitoring
helm install prometheus prometheus-community/kube-prometheus-stack \
  --version 88.5.4 --namespace monitoring

# ServiceMonitor (from repo, applied to cluster)
kubectl kustomize clusters/alpha | kubectl apply -f -
```

## Verified / observed

- KEDA operator + admission-webhooks + metrics-apiserver `1/1` in `keda`.
- `scaledobjects.keda.sh`, `scaledjobs.keda.sh`, `triggerauthentications.keda.sh`
  CRDs present.
- kube-prometheus-stack pods all Running in `monitoring`; Prometheus v3.14.0
  `Reconciled=True`.
- Services up: Prometheus `9090`, Grafana `80`, Alertmanager `9093`.
- `ServiceMonitor minecraft-servers` created in `prd-games-42wasd-admin`; the
  alpha kustomize build renders it and Prometheus selects it by
  `release: prometheus`.
- Added `keda: 2.20.2` and `kube_prometheus_stack: 88.5.4` to
  `verified-versions.yaml`.
- Marked phase 4 `done` in `progress.yaml` and regenerated
  `docs/implementation/index.md`.

## Outcome

KEDA and the Prometheus/Grafana stack are up; the scrape target exists. Next:
Phase 5 — Deploy CockroachDB and Nakama.