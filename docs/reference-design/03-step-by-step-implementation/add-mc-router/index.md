# Add mc-router

Use `mc-router` for cases where players enter through different hostnames or sleeping services should wake at the edge.

Example:

```text
survival.example.com
map-123.example.com
```

`mc-router` can discover annotated Kubernetes services. Its native Kubernetes
auto-scale (0↔1) targets **StatefulSet** backends (or Docker containers) only —
it does **not** scale an OpenKruiseGame `GameServerSet` directly. For the
dynamic worlds in this design, use its **webhook integration** to notify the
World Controller to wake the `GameServerSet` (this is the canonical path —
see the two traffic paths below). It can also use a proxy server name so the
final player route still goes to Velocity after the backend is awakened.

---

## Two distinct wake paths

**Path 1 — a new hostname connection at the edge** (mc-router sees it):

```text
client --(hostname)--> mc-router
        ↓
   wake webhook
        ↓
   World Controller
        ↓
   GameServerSet 0 -> 1
        ↓
   route to Velocity / backend
```

**Path 2 — an already-connected player switching in-game** (no new public
handshake):

```text
player in Velocity -> walks into portal
        ↓
   Velocity NetworkBridge -> World Controller directly
        ↓
   ensure-ready + transfer
```

For Path 2 there is **no** incoming connection for mc-router to observe, so the
wake/readiness must be performed by the World Controller before Velocity
transfers the player. mc-router handles the edge; the World Controller is the
authoritative in-game lifecycle owner.

---

## Why World Controller still remains

```text
mc-router = edge wake/routing (webhook -> World Controller for GameServerSet)
World Controller = authoritative in-game lifecycle + sole replica owner
```

A **named persistent world's** replicas are owned by the World Controller, so
`mc-router` never scales the GameServerSet directly — it only fires the webhook.
For **pooled** capacity a KEDA `ScaledObject` may own replicas instead.

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
