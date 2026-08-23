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

The per-server status metrics (`online`, `latency`, `MOTD`) and the map
`status/ping` readiness probe come from the same maintained agent —
**itzg/mc-monitor** — exported to Prometheus, so the readiness and the metrics
are one trusted source.

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
