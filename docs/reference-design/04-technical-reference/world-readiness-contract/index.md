# World readiness contract

World Controller returns READY only when:

```text
GameServerSet desired replicas >= 1
Pod Ready
Service endpoints exist
Minecraft status check succeeds
runtime revision matches expected revision
server is not draining
capacity reservation is available
```

This contract is more useful than a generic `/healthz`.

The Minecraft `status/ping` step of this contract is provided by a maintained
probe agent — **itzg/mc-monitor** (`status` subcommand) — rather than
hand-rolled ping code in the World Controller. `mc-monitor` also exports the
same status (online count, latency, MOTD) as Prometheus/Influx metrics, so the
readiness probe and the perf metrics share one trusted source.

---
