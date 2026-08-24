# Monitoring

The Prometheus/Grafana stack is installed in
[Phase 4 — install-keda-and-observability](../install-keda-and-observability/index.md).
This phase configures what to scrape and what to alert on.

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

The per-server status metrics (`online` count, response latency) and the map
`status/ping` readiness probe come from the same maintained agent —
**itzg/mc-monitor** — exported to Prometheus, so the readiness and the metrics
are one trusted source.

> **mc-monitor scope:** it reports Minecraft *reachability* — status response,
> ping/response latency, online/max-count observation. It does **not** export
> TPS, MSPT, or tick/GC health; those come from backend/NetworkBridge telemetry
> plus spark profiling. It also does **not** export MOTD.

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
