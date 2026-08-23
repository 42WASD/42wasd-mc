# MapInstance schema

```json
{
  "map_id": "fantasy-kingdom-001",
  "runtime_id": "fantasy-1.20.1-forge",
  "state": "READY",
  "backend_id": "fantasy-kingdom-001",
  "service_host": "fantasy-kingdom-001.minecraft.svc.cluster.local",
  "port": 25565,
  "players": 4,
  "reservations": 1,
  "max_players": 12,
  "last_activity": "2026-08-19T...",
  "revision": 14
}
```

`state` uses the **operational (Axis-2)** vocabulary from
[routing-state-machine](../routing-state-machine/index.md): `ASLEEP`,
`STARTING`, `READY`, `STOPPING`, `ERROR`. It is the world's long-lived health,
**not** a routing-request state (`REQUESTED`/`TRANSFERRING`/`COMPLETE` belong
to a per-join operation and are not stored here).

`reservations` counts seats already promised to joining players/parties but
not yet connected; see `random-routing-scoring` and `reservations` semantics.

Use a revision/version for optimistic concurrency if state is persisted outside Kubernetes.

---
