# Phase 26 — Monitoring

Use your existing Prometheus/Grafana stack.

World Controller metrics:

```text
minecraft_world_start_seconds
minecraft_world_start_failures_total
minecraft_world_ready
minecraft_world_players
minecraft_world_reservations
minecraft_route_requests_total
minecraft_route_failures_total
```

Proxy:

```text
connected players
backend connection failures
transfer latency
```

Minecraft server:

```text
TPS
MSPT
heap
CPU
memory
disk
```

Alert on:

```text
world startup failures
repeated crash loop
disk pressure
PVC nearly full
CockroachDB unavailable
Nakama unavailable
Velocity backend failure spike
```

---
