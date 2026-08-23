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

Lifecycle (Axis-2 operational states; matches `mapinstance-schema`):

```text
ASLEEP
   ↓ request
STARTING
   ↓ pod Ready + Minecraft ping Ready
READY (draining = qualifier while winding down)
   ↓ no players / idle timeout (draining -> save + stop)
STOPPING
   ↓ save + stop
ASLEEP
```

`draining` is a separate flag on `READY` (not a state value); a world that is
`READY` but draining is being wound down for scale-to-zero. The PVC remains
while replicas become zero.

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
