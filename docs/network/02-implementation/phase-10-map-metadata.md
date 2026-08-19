# Phase 10 — Define map metadata

Example:

```yaml
apiVersion: platform.example/v1
kind: MapDefinition

metadata:
  id: backrooms-level-0
  displayName: "Backrooms — Level 0"
  creatorId: "user-123"

spec:
  runtimeId: backrooms-current

  persistence: persistent

  capacity:
    maxPlayers: 12

  routing:
    public: true
    randomEligible: true
    allowPartyJoin: true
    weight: 1.0

  tags:
    - horror
    - backrooms
    - community

  world:
    pvc: backrooms-level-0-world

  idle:
    sleepAfterSeconds: 600
```

Separate the two concepts:

```text
MapDefinition = what the world is
MapInstance   = current running state
```