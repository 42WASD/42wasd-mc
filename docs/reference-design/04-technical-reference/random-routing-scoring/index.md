# Random routing scoring

Do not use pure random if maps differ in health and capacity.

## Input fields (from MapInstance + MapDefinition)

The scoring code reads these fields. Their source is noted where they live in
[mapinstance-schema](../mapinstance-schema/index.md) or
[define-map-metadata](../../03-step-by-step-implementation/define-map-metadata/index.md).

| Field            | Type    | Source         | Meaning                                                        |
|------------------|---------|----------------|----------------------------------------------------------------|
| `enabled`        | bool    | MapDefinition  | world may be routed to at all (the World Controller guard)     |
| `runtime_id`     | string  | MapDefinition  | compatibility gate; must equal player's runtime                |
| `routing.public` | bool    | MapDefinition  | whether the map is exposed to the random portal / world browser |
| `random_eligible`| bool    | MapDefinition  | whether the map can be chosen by the random portal at all      |
| `weight`         | float   | MapDefinition  | relative promotion among eligible maps (community/manual boost)|
| `free_slots`     | int     | derived        | `max_players - players - reservations` (see below)             |
| `freshness`      | derived | derived        | how recently updated/maintained; decays over age               |
| `reachability`   | derived | mc-monitor     | protocol reachability (status/ping success + latency)          |
| `tick_health`    | derived | backend telemetry | TPS/MSPT/tick health from backend plugin/bridge (+ spark)  |
| `capacity`       | derived | WC reservation | how many free slots vs a threshold — prefer underused (authoritative World Controller reservation state) |
| `novelty`        | derived | per-player     | how long since this player last visited — prefer not-recent    |

`free_slots` is always **derived**, never stored: `max_players - players -
reservations`. Keep it in sync with `reservations` (see reservations semantics
below) so a reservation doesn't over-admit a party that then can't fit.

> **Source split.** mc-monitor contributes *reachability* (can the server be
> pinged, how fast) — it does **not** measure TPS/MSPT. `tick_health` comes from
> backend telemetry (NetworkBridge/plugin exporting tick health) plus spark for
> profiling. `capacity` comes from the authoritative World Controller
> reservation state, not from a probe.

### Factor bounds and the reachability gate

Each factor is a value in **[0, 1]** (0 excludes, 1 neutral/no penalty) and the
final score is their product times the base `weight`. A factor at 0 forces the
score to 0.

**`reachability_factor` is a hard gate, not just a down-weight:** any map whose
reachability/ping is failing (`reachability_factor == 0`) is **excluded**,
regardless of how high its other scores are. The remaining factors only *rank*
among the gated-eligible set. This keeps an unreachable map from ever being
selected just because it is new, promoted, or underused. Concretely:

```text
reachability_factor = 0      -> excluded (gate), regardless of weight/freshness/novelty
reachability_factor in (0,1] -> down-weights relative to other healthy maps
```

`tick_health_factor` (backend telemetry) and `capacity_factor` (World Controller
reservation state) further rank, but they are not the reachability gate.

Because the factors are bounded to [0,1], no factor can be negative or >1, so
the weighted-random selection always sees a well-formed probability mass.

Example:

```python
eligible = [
    m for m in maps
    if m.enabled
    and m.runtime_id == player.runtime_id
    and m.routing.public           # only maps exposed to the portal
    and m.random_eligible
    and m.free_slots >= party_size
    and m.reachability_factor > 0  # hard gate (mc-monitor)
]

for m in eligible:
    score = (
        m.weight
        * freshness_factor(m)          # in [0,1]
        * m.reachability_factor        # in (0,1]; 0 already gated out
        * m.tick_health_factor(m)      # in [0,1] (backend telemetry)
        * capacity_factor(m)           # in [0,1] (WC reservation state)
        * novelty_factor(player, m)    # in [0,1]
    )

selected = weighted_random(eligible, score)
```

This lets you prefer:

```text
reachable
tick-healthy
underused (authoritative capacity)
new
not recently visited
community-promoted
```

without violating compatibility and without ever selecting an unreachable map.

---

## Reservations semantics (how free_slots is computed)

A reservation is a **seat promise**, not a connection. When the World Controller
starts to route a player or party toward a world, it reserves seats so the world
does not over-admit while the party is still loading/transferring.

```text
free_slots = max_players - players - reservations
```

- `players` = currently connected (observed from mc-monitor / backend).
- `reservations` = seats promised to in-flight joins not yet connected.
- A map is `eligible` for a party only if `free_slots >= party_size`.

Invariants:

```text
reservations >= 0
players + reservations <= max_players   (never over-commit a starting world)
```

On transfer success, `players` increases and the reservation is consumed; on
failure or timeout, the reservation is released. Releasing must be idempotent
(guard with the revision token) so a duplicate release can't under-count.

Why reserve at all: without reservations, two parties could both see a last
free slot, both wake/transfer, and the second over-admits. Reservations make
the slot-counting linearizable before the backend ever connects anyone.

---
