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
scale StatefulSet to 0
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
