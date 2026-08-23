# World readiness contract

The World Controller's `ensure-ready` returns READY only when:

```text
GameServerSet desired replicas >= 1
Pod Ready
Minecraft status check succeeds
```

A fuller, staging-time contract can additionally require:

```text
backend registered with the proxy
Service endpoints exist
runtime revision matches expected revision
server is not draining
capacity reservation is available
```

The first block is what `ensure-ready` currently implements (two-stage:
Pod Ready, then Minecraft `status/ping`). The second block are the safeguards
you add once invites, draining, and reservations are in place. Keep the two
blocks labeled so the implementation and the contract do not drift.

This contract is more useful than a generic `/healthz`.

The Minecraft `status/ping` step of this contract is provided by a maintained
probe agent — **itzg/mc-monitor** (`status` subcommand) — rather than
hand-rolled ping code in the World Controller. `mc-monitor` also exports the
same status (online count, latency, MOTD) as Prometheus/Influx metrics, so the
readiness probe and the perf metrics share one trusted source.

---
