# Routing state machine

There are **two** state machines that readers must not conflate. They live on
different axes and answer different questions.

## Axis 1 — The routing request machine (per join/transfer action)

This is the lifecycle of a single "move this player to a world" operation. It
is per-request, short-lived, and ends in a terminal state (`COMPLETE`,
`FAILED`, or `CLIENT_TRANSITION_REQUIRED`).

```text
REQUESTED
    │
    ├── incompatible runtime ─────► CLIENT_TRANSITION_REQUIRED
    │
    └── compatible
            │
            ▼
         RESERVING
            │
            ▼
         STARTING
            │
            ▼
     WAITING_K8S_READY
            │
            ▼
      WAITING_MC_READY
            │
            ▼
        REGISTERING
            │
            ▼
         TRANSFERRING
            │
            ├── success ─────────► COMPLETE
            │
            └── failure ─────────► RELEASE_RESERVATION -> FAILED
```

Every stage should have timeout/error handling.

## Axis 2 — The world operational state machine (persistent, per world)

This is the long-lived state of a `MapInstance`. It is what `MapInstance.state`
refers to, and it must NOT be one of the Axis-1 states. The `READY` value seen
in `mapinstance-schema` is this axis, not a routing-request terminal.

```text
ASLEEP            replicas=0, no process, PVC retained
  │
  ▼
STARTING          replicas>=1, K8s pod not ready yet (or MC not ready)
  │
  ▼
READY             pod ready + Minecraft status/ping OK + backend registered
  │
  ├── draining    (a sub-state of READY: winding down for scale-to-zero)
  │
  ▼
STOPPING          saving/stopping gracefully, safe-to-stop verified
  │
  ▼
ASLEEP            back to replicas=0
  │
  └── ERROR/UNHEALTHY (crashed, stuck startup) — operator/SRE attention
```

The two machines interlock at exactly one point:

```text
Axis 1 TRANSFERRING  ==>  requires Axis 2 == READY (or becomes READY first)
```

In other words, the routing machine drives a world *toward* `READY`, but only
the operational machine *is* `READY`. A routing request can complete
(`COMPLETE`) while the world remains in `READY` indefinitely — they are
independent lifetimes.

---

## State vocabulary (summary)

| Term          | Axis | Meaning                                                    |
|---------------|------|------------------------------------------------------------|
| `REQUESTED`…`FAILED` | 1 (routing) | A single join/transfer operation |
| `READY`       | 2 (operational) | World is acceptive + registered; can be joined |
| `ASLEEP`      | 2 (operational) | scaled to 0, PVC kept; wake on demand |
| `STARTING` / `STOPPING` | 2 (operational) | in-flight world startup/shutdown |
| `CLIENT_TRANSITION_REQUIRED` | 1 (routing) | wrong runtime; launcher handoff needed |

Do not store `REQUESTED`/`TRANSFERRING` (Axis 1) in `MapInstance.status`; store
Axis-2 operational state there. Keep the two vocabularies separate to avoid
treating a routed-request state as the world's health.

---
