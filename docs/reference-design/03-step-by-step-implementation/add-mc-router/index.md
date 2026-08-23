# Add mc-router

Use `mc-router` for cases where players enter through different hostnames or sleeping services should wake at the edge.

Example:

```text
survival.example.com
map-123.example.com
```

`mc-router` can discover annotated Kubernetes services. Its built-in auto-scale
(0↔1) targets `StatefulSet` backends (or Docker containers) only — it does not
scale an OpenKruiseGame `GameServerSet` directly. For the dynamic worlds in this
design, use its webhook integration to notify the World Controller to wake the
`GameServerSet` (KEDA + `ScaledObject` is an alternative scale trigger).

It can also use a proxy server name so the final player route still goes to Velocity after the backend is awakened.

---

## Why World Controller still remains

New external connection:

```text
client -> mc-router -> wake -> Velocity
```

Existing connected player:

```text
player in Velocity -> portal
```

The second path bypasses the public edge handshake.

Therefore:

```text
mc-router = edge wake/routing
World Controller = authoritative in-game lifecycle
```

If the 0→1 edge wake should be event-driven rather than polled, **KEDA**
(`ScaledObject` → HPA on the GameServerSet) can serve as the scale trigger
alongside mc-router, while the World Controller still owns the safe-to-stop
logic on scale-down.

---

## Prefer webhook isolation if desired

`mc-router` supports webhook integration.

A hardened design can keep Kubernetes mutation permission in the World Controller rather than giving `mc-router` broad credentials.

Pattern:

```text
mc-router
   ↓ webhook
World Controller
   ↓ K8s
```

---
