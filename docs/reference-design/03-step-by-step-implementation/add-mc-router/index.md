# Add mc-router

Use `mc-router` for cases where players enter through different hostnames or sleeping services should wake at the edge.

Example:

```text
survival.example.com
map-123.example.com
```

`mc-router` can discover annotated Kubernetes services and can scale a GameServerSet from 0 to 1.

It can also use a proxy server name so the final player route still goes to Velocity after the backend is awakened.

---

## 37.1 Why World Controller still remains

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

## 37.2 Prefer webhook isolation if desired

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
