# Add idle sleep

For persistent worlds:

```text
last player leaves
    ↓
start idle timer
    ↓
new reservation?
  yes -> cancel sleep
  no  -> continue
    ↓
request graceful save/stop
    ↓
wait process exit
    ↓
scale GameServerSet to 0
```

Do not `SIGKILL` an actively saving world as your normal sleep method.

---

## Separate “empty” from “safe to stop”

A server may be empty but still:

```text
saving
running maintenance
executing a migration
reserved for a joining party
```

Track:

```text
player_count
reservation_count
draining
maintenance_lock
```

Sleep only when all permit it.

---

## The World Controller is the sole replica owner for named worlds

For a **named persistent world**, the World Controller owns the 0↔1 replica
transition **itself** — via the GameServerSet `/scale` subresource — driven by
the idle/player-count/reservation signals above. It does **not** delegate that
world's replicas to KEDA.

```text
KEDA / ScaledObject      -> POOLED capacity only (worlds WC does NOT own)
World Controller         -> named persistent world replicas (0/1) + safe-to-stop
```

So for the named-world sleep path the trigger *is* the World Controller (idle
timer + safe-to-stop checks), and the scale-out on demand is the World
Controller (on join/invite/portal). KEDA is only used where the 0↔ transition
applies to pooled capacity. Never attach a `ScaledObject` to a
World-Controller-owned `GameServerSet` (see the
[recommended-source-of-truth-model](../../04-technical-reference/recommended-source-of-truth-model/index.md)
replica-owner rule).

---

## What the World Controller needs to observe

For each named world the World Controller needs the same signals it already
tracks:

```text
player_count
reservation_count
draining
maintenance_lock
```

and must gate sleep (replicas → 0) on all of them, and gate wake (replicas → 1)
on an explicit join/invite/portal request. The graceful save/shutdown steps
(quiesce → save → confirm exit → scale 0) live entirely in the World Controller.
