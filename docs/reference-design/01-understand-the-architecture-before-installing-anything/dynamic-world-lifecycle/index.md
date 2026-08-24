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

### 8.1.1 Always-on / never-sleep worlds

Scale-to-zero is the **default** for idle persistent worlds, but it is not
mandatory. A `MapDefinition`/`RuntimeDefinition` may opt out of sleeping:

```text
always_on: true   # never scale the GameServerSet to 0, even with no players
```

Use this for worlds that must keep simulating with **no human players**:

- a colony world whose autonomous entities (e.g. MineColonies citizens) keep
  progressing;
- a simulation world with self-piloting / living entities that shape the
  terrain over time;
- a world where an **LLM "director"** autonomously drives events, spawns new
  entities, or even introduces new content between player visits.

When `always_on: true` the world stays `READY` (replicas `1`) permanently;
the idle-drain path (and KEDA's scale-to-zero trigger) is disabled for it. This
is a deliberate cost trade-off — the world consumes a node + JVM + PVC IO
24/7 — so it should be reserved for worlds where background simulation is a
product requirement, not a default. All other persistent worlds still default
to idle-sleep.

> **LLM-director content changes are a runtime revision, not a hot-swap.**
> If a director wants to add new mods/entities, that changes the required
> client runtime. Per the runtime-class rule, this must be versioned as a new
> runtime revision (e.g. `fantasy-1.20.1-r3` → `r4`) and rolled out with the
> launcher-driven client update — an always-on world can evolve *world content*
> and *server-side logic* live, but changing *client-required mods* still goes
> through the normal revision/rollout path. See
> [upgrade-policy](../../04-technical-reference/upgrade-policy/index.md) and
> `packwiz`/Modrinth Server Project.

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
