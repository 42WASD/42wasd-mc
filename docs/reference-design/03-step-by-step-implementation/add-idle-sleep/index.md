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

## 38.1 Separate “empty” from “safe to stop”

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

## 38.2 Trigger the scale transition with a maintained scaler

The World Controller owns the *safe-to-stop decision* above. It does not need
to hand-roll the 0↔ scale *trigger* — **KEDA** (CNCF-graduated) can express the
idle / player-count scaler as a `ScaledObject` that drives the GameServerSet
through the `/scale` subresource. This separates:

```text
KEDA                 -> decides WHEN to scale (idle timer / player count)
World Controller     -> decides whether it is SAFE to stop (reservations,
                       draining, maintenance) and drives graceful save
```

KEDA is the trigger; the World Controller stays the authority on product
semantics. Use KEDA only where the 0↔ transition is event/condition driven;
keep the reservation/save gating in the World Controller.
