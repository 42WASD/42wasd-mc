# Step 9 — Persistent StatefulSet scale-to-zero map

Make a single world's backend **scale to zero** when idle and **wake** when a player wants to play it — while keeping its world data persistent. This is the core "scale-to-zero dynamic map" behavior.

## Goal

A map backend with `replicas: 0` when nobody is playing, woken on demand with its persisted world data intact.

## Design

Use a **Persistent StatefulSet** per world (or a single StatefulSet with per-pod worlds):

- World data lives in a **PVC** (persistent volume) — this survives scale-to-zero.
- The pod is scaled to `0` when idle (controller / a sleeping sidecar decides).
- A player request triggers a **wake**: the controller scales the StatefulSet to `1`.
- While waking, the player is held in the lobby or a waiting state.

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: backrooms-001
  namespace: minecraft
spec:
  serviceName: backrooms-001
  replicas: 0   # idle -> sleep
  selector:
    matchLabels:
      app: backrooms-001
  template:
    metadata:
      labels:
        app: backrooms-001
    spec:
      containers:
        - name: minecraft
          image: itzg/minecraft-server:2026.8.0
          volumeMounts:
            - name: world
              mountPath: /data
      volumes: ...
```

## Wake flow

1. Player requests map X via portal or `/join`.
2. Controller looks up X → sees sleeping backend.
3. Controller scales StatefulSet `replicas 0 → 1` and waits for `Ready`.
4. Backend becomes ready; controller records it as `running`.
5. Proxy transfers the player (Step 10).

## Idle → sleep

When no players are on the backend for an idle timeout, scale back to `0`. Optionally disconnect stragglers with a countdown message.

## Acceptance criteria

```text
[ ] world data persists across sleep/wake (PVC)
[ ] sleeping backend has 0 replicas (no cost while idle)
[ ] wake returns the same world data
[ ] no data loss on repeated scale-to-zero cycles
[ ] readiness gates prevent transferring before the world is ready
```

## Next step

[Step 10 — Portal → wake → transfer](step-10-portal-wake-transfer.md)