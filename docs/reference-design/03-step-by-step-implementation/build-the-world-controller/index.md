# Build the World Controller

Choose a boring implementation language you operate well.

Good options:

```text
Go
Python/FastAPI
Kotlin/Java
```

The service is not latency-critical compared with Minecraft startup time.

Correctness matters more.

---

## Minimal API

Start with:

```http
GET /v1/maps
GET /v1/maps/{map_id}
GET /v1/instances/{map_id}

POST /v1/instances/{map_id}/ensure-ready
POST /v1/instances/{map_id}/reserve
POST /v1/routes/random
POST /v1/instances/{map_id}/release
```

Do not begin with 50 endpoints.

---

## `ensure-ready`

Pseudo-code:

```python
async def ensure_ready(map_id):
    map_def = catalog.get(map_id)

    assert map_def.enabled

    runtime = runtimes.get(map_def.runtime_id)

    gss = k8s.get_gameserverset(map_def.map_id)   # instance_name == map_id

    if gss.spec.replicas == 0:
        k8s.scale_gameserverset(gss, 1)

    await wait_for_pod_ready(gss)
    await wait_for_minecraft_ready(map_def.service_host, 25565)

    await proxy_registry.ensure_registered(
        server_id=map_def.map_id,
        address=map_def.service_host
    )

    return {
        "state": "READY",
        "map_id": map_def.map_id,
        "runtime_id": runtime.id,
        "service_host": map_def.service_host,
        "port": 25565
    }
```

This operation must be idempotent.

The 0->1 scale of the GameServerSet is the one transition a maintained scaler
can own. OpenKruise's "Gameservers Scale" guide shows a KEDA `ScaledObject`
whose `scaleTargetRef` points directly at the GameServerSet
(`apiVersion: game.kruise.io/v1alpha1, kind: GameServerSet`) with
`minReplicaCount: 0`. KEDA provides the 0<->1 edge; the World Controller still
owns the *decision* to wake (reservations, invites, readiness) and calls the
GameServerSet `/scale` path directly for product-driven wakes.

---

## Readiness is two-stage

Kubernetes readiness:

```text
Pod Ready
```

Minecraft readiness:

```text
status/ping succeeds
```

Use both.

For Forge, startup can take substantially longer than a small Paper map.

Set per-runtime startup timeout.

The Minecraft `status/ping` probe is provided by a maintained agent —
**itzg/mc-monitor** (`status` subcommand) — rather than hand-rolled ping code.
`mc-monitor` doubles as the Prometheus/Influx metrics exporter, so the
readiness probe and the per-map perf metrics (TPS, latency, player count) share
one trusted source.

---

## RBAC

World Controller ServiceAccount should have only what it needs.

Example intent:

```yaml
rules:
  - apiGroups: ["game.kruise.io"]
    resources: ["gameserversets", "gameservers"]
    verbs: ["get", "list", "watch", "patch", "update"]

  - apiGroups: [""]
    resources: ["pods", "services"]
    verbs: ["get", "list", "watch"]
```

Adjust to exact Kubernetes API behavior and your implementation.

Do not grant cluster-admin.

---
