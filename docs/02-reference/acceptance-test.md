# Acceptance test

An end-to-end test that validates the whole system works as documented. Run this after building the network (and after major upgrades).

## Test matrix

### T1 — Static join (Steps 1-2)

```text
[ ] vanilla client connects through the proxy
[ ] lands in the lobby
[ ] UUID seen by backend matches authenticated UUID
[ ] backend is not directly reachable publicly
```

### T2 — Protocol translation (Step 4)

```text
[ ] an older-version client connects through the proxy
[ ] reaches a compatible backend without a protocol error
```

### T3 — Social (Steps 5-6)

```text
[ ] player identity maps to a stable Nakama ID
[ ] friend add/remove/list works
[ ] party create/invite works
```

### T4 — /join (Step 7)

```text
[ ] `/join survival-main` transfers a player
[ ] `/join lobby` returns them
[ ] unknown backend gives a clear error
```

### T5 — Dynamic wake (Steps 8-10)

```text
[ ] sleeping map scales to 0 when idle
[ ] portal wakes the map (0 → 1)
[ ] player is held during wake, then transferred
[ ] world data persists across wake cycles
```

### T6 — Runtime compatibility (Steps 12-13, 15)

```text
[ ] random map never violates the runtime invariant
[ ] fantasy runtime joins `fantasy-1.20.1-forge` backends
[ ] vanilla client is correctly blocked/advised for fantasy maps
[ ] cross-runtime invite separates policy from runtime
```

### T7 — Edge (Step 16)

```text
[ ] public host routes through mc-router
[ ] connecting to a sleeping backend triggers wake, not disconnect
```

### T8 — Community upload (Step 17)

```text
[ ] a valid map upload is validated and registered
[ ] an invalid/incompatible map is rejected
```

## Passing rule

A step's acceptance criteria must pass before you move to the next step. See each [step](../01-implement/index.md) page for its criteria.

## See also

- [Operations: monitoring](../03-operations/monitoring.md)