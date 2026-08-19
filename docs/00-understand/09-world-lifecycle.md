# Dynamic world lifecycle

Two lifecycle types.

## Persistent worlds

**Examples:** main survival, player-owned worlds, long-running community worlds, MineColonies colony worlds.

**Use:** `StatefulSet + stable Service + PVC + replicas 0 or 1`.

```text
SLEEPING → (request) → STARTING → (Pod Ready + Minecraft Ready) → READY
  → (reservation) JOINABLE → (idle timeout) DRAINING → (save + stop) SLEEPING
```

The PVC persists while replicas go to zero.

## Ephemeral session worlds

**Examples:** Backrooms run from an immutable template, temporary minigame, one-session dungeon, short-lived challenge.

**Use Agones** when you want a warm pool, atomic allocation, session lifecycle, autoscaling, and discard-after. Do **not** force long-lived worlds into Agones.

## The two are different

| | Persistent | Ephemeral |
|---|---|---|
| Workload | StatefulSet + PVC | Agones Fleet |
| Replicas | 0 or 1 | N (warm pool) |
| Data | Durable, survives stop | Discarded |
| Example | Survival world | Backrooms run |