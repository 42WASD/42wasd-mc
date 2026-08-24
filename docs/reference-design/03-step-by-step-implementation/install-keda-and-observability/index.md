# Install KEDA and the observability stack

Two things the later phases assume are present but that no step actually
installs:

1. **KEDA** — the event-driven autoscaler that fires the `GameServerSet`
   0↔1 transition (referenced by `build-the-world-controller`,
   `add-mc-router`, and `add-idle-sleep`).
2. **The Prometheus/Grafana stack** — the destination for
   `itzg/mc-monitor`'s exported metrics, and the alerting home for the
   `monitoring` phase.

> `mc-monitor` itself is *embedded in each Minecraft server image* (you add
> the agent as a sidecar/process in the runtime), not installed cluster-wide.
> This phase installs the *platform* pieces: KEDA + Prometheus + Grafana.

---

## Install KEDA

KEDA is CNCF-graduated. Install the operator via Helm:

```bash
helm repo add kedacore https://kedacore.github.io/charts/
helm repo update
helm install keda kedacore/keda --namespace keda --create-namespace
```

Verify the operator is up:

```text
kubectl get deploy -n keda
NAME                READY   UP-TO-DATE   AVAILABLE
keda-operator       1/1     1            1
keda-operator-metrics-apiserver   1/1   1            1
```

KEDA 0↔1 semantics matter here: a `ScaledObject` with `minReplicaCount: 0`
scales the target to zero when its scaler is inactive and scales back to 1 on
the next poll when it becomes active. The `activationThreshold`/`cooldownPeriod`
values decide *when* 0↔1 happens — that is KEDA's "when", which stays
separate from the World Controller's "safe to stop" decision (see
`add-idle-sleep`).

> **Replica-owner rule.** KEDA may scale a workload that *it* owns. In this
> design that means **pooled capacity** (warm session fleets). A **named
> persistent world** is **not** a KEDA target: the World Controller is the sole
> replica owner for its `GameServerSet`, so it does **not** get a
> `ScaledObject` — even for idle sleep. Do not point a KEDA `ScaledObject` at a
> World-Controller-owned GameServerSet. Only pooled GameServerSets the World
> Controller does not own get KEDA autoscaling.

---

## Install Prometheus + Grafana

Install a standard stack (e.g. the kube-prometheus-stack umbrella chart):

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace
```

This brings in Prometheus, Alertmanager, and Grafana. Adjust storage class and
retention for your cluster; do not leave the default ephemeral storage if you
want durable alert history.

Verify Prometheus can scrape:

```text
kubectl get svc -n monitoring prometheus-kube-prometheus-prometheus
```

---

## Configure the mc-monitor scrape target

`mc-monitor` exports Prometheus metrics from inside each server. The server
pods should be reachable by a Prometheus `ServiceMonitor` (or a pod
annotation) so the metrics the `monitoring` phase lists (TPS, MSPT, player
count, readiness) are actually collected.

Placeholder `ServiceMonitor` targetting the minecraft namespace:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: minecraft-servers
  namespace: minecraft
spec:
  selector:
    matchLabels:
      app.kubernetes.io/part-of: minecraft
  endpoints:
    - port: metrics
```

Scrape configuration is per-runtime; this phase establishes that the endpoints
and RBAC exist, and the concrete per-map scrape selectors are finalized in the
`monitoring` phase.

---

## Acceptance

```text
kubectl get scaledobject -A          # KEDA can create ScaledObjects (0)
kubectl get svc -n monitoring        # prometheus + grafana up
kubectl get servicemonitor -n minecraft minecraft-servers   # scrape target exists
```

None of these existed before this phase; adding them closes the gap where
`build-the-world-controller`, `add-mc-router`, `add-idle-sleep`, and
`monitoring` all assumed a scaler and an alerting backend without one ever
being installed.

---

## Relationship to the World Controller

KEDA owns the *trigger* (when to scale). The World Controller owns the
*decision* (whether it is safe to stop, and product-driven wakes for
reservations/invites/readiness). Installing KEDA here gives the World
Controller a real `/scale` target to drive and lets `add-idle-sleep` rely on a
maintained scaler rather than hand-rolled polling.