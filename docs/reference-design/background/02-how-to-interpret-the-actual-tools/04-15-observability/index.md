# Observability

Track per world:

```text
state
players
reserved_slots
runtime_id
start latency
Minecraft-ready latency
last activity
idle duration
CPU
memory
tick time / MSPT
TPS
disk usage
save duration
```

Track routing:

```text
invite accept latency
world wake success rate
world wake p50/p95
portal transfer success
random-map selection count
failed compatibility checks
launcher-transition count
pending-invite completion rate
```

Track proxy:

```text
connected players
backend connection failures
protocol translation failures
Forge handshake failures
transfer latency
```

Track social:

```text
party creation
invite acceptance
pending invite expiry
presence update failures
```

The most useful product metric is:

```text
time from "Join friend" click
to "player can move in friend's world"
```

Measure it separately for:

```text
same runtime / awake world
same runtime / sleeping world
cross-runtime install+launch
```

---
