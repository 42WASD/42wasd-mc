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

Use a revision/version for optimistic concurrency if state is persisted outside Kubernetes.

---
