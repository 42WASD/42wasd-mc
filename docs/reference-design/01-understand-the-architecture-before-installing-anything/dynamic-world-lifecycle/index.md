# Dynamic world lifecycle

Use two different lifecycle types.

## 8.1 Persistent worlds

Examples:

```text
main survival
player-owned world
long-running community world
MineColonies colony world
```

Use:

```text
OpenKruiseGame GameServerSet
+ stable Service
+ PVC (via VolumeClaimTemplates)
+ replicas 0 or 1
+ podUpdatePolicy: InPlaceIfPossible
```

Lifecycle:

```text
SLEEPING
   ↓ request
STARTING
   ↓ pod Ready + Minecraft ping Ready
READY
   ↓ reservation
JOINABLE
   ↓ no players / idle timeout
DRAINING
   ↓ save + stop
SLEEPING
```

The PVC remains while replicas become zero.

---

## 8.2 Ephemeral session worlds

Examples:

```text
Backrooms run generated from immutable template
temporary minigame
one-session dungeon
short-lived challenge
```

Use Agones when you genuinely want:

```text
warm pool
atomic allocation
session lifecycle
autoscaling fleet
discard instance afterward
```

Do not force long-lived player worlds into Agones merely because Agones is a game-server operator.

---
