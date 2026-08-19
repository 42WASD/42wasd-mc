# Phase 11 — Build the World Controller

Choose a boring implementation language you operate well: Go, Python/FastAPI, or Kotlin/Java. The service is not latency-critical compared with Minecraft startup time. Correctness matters more.

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

## `ensure-ready`

Pseudo-code:

```python
async def ensure_ready(map_id):
    map_def = catalog.get(map_id)
    assert map_def.enabled

    runtime = runtimes.get(map_def.runtime_id)
    sts = k8s.get_statefulset(map_def.instance_name)

    if sts.spec.replicas == 0:
        k8s.scale_statefulset(sts, 1)

    await wait_for_pod_ready(sts)
    await wait_for_minecraft_ready(map_def.service_host, 25565)

    await proxy_registry.ensure_registered(
        server_id=map_def.id,
        address=map_def.service_host
    )

    return {"state": "READY", "server_id": map_def.id, "runtime_id": runtime.id}
```

This operation must be **idempotent**.

## Readiness is two-stage

Kubernetes readiness (`Pod Ready`) **and** Minecraft readiness (`status/ping succeeds`). Use both. For Forge, startup can take substantially longer than a small Paper map — set a per-runtime startup timeout.

## RBAC

The World Controller ServiceAccount should have only what it needs:

```yaml
rules:
  - apiGroups: ["apps"]
    resources: ["statefulsets", "statefulsets/scale"]
    verbs: ["get", "list", "watch", "patch", "update"]

  - apiGroups: [""]
    resources: ["pods", "services"]
    verbs: ["get", "list", "watch"]
```

Do not grant cluster-admin.