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
same status (online count, latency, MOTD) as Prometheus/Influx metrics.

**Scope of mc-monitor (readiness, not performance):** mc-monitor reports
*Minecraft protocol reachability* — status response, ping/response latency, and
the current/max online-player observation. It does **not** measure TPS, MSPT,
or tick health. Those come from backend/NetworkBridge telemetry (a server-side
plugin/bridge exporting tick health) plus spark for profiling/diagnostics. So:

```text
readiness + reachability   <- mc-monitor (status/ping, online count, latency)
tick health / TPS / MSPT    <- backend telemetry (NetworkBridge/plugin) + spark
capacity                    <- World Controller reservation state
```

Keep these sources separate; do not present mc-monitor as the TPS/performance
system.

---
