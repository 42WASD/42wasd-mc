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

## 28.1 Minimal API

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

## 28.2 `ensure-ready`

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

    return {
        "state": "READY",
        "server_id": map_def.id,
        "runtime_id": runtime.id
    }
```

This operation must be idempotent.

---

## 28.3 Readiness is two-stage

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

---

## 28.4 RBAC

World Controller ServiceAccount should have only what it needs.

Example intent:

```yaml
rules:
  - apiGroups: ["apps"]
    resources: ["statefulsets", "statefulsets/scale"]
    verbs: ["get", "list", "watch", "patch", "update"]

  - apiGroups: [""]
    resources: ["pods", "services"]
    verbs: ["get", "list", "watch"]
```

Adjust to exact Kubernetes API behavior and your implementation.

Do not grant cluster-admin.

---
