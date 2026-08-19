# Step 12 — Random compatible map

Add a "random map" feature: pick a compatible map at random, ensuring the chosen map is valid for the requester's runtime class, and wake/send the player there.

## Goal

A player requests a random map, and gets a compatible map (matching their client runtime) selected and prepared.

## Compatibility = runtime class

The controller selects only from maps whose **runtime class** matches the requester's runtime (Step 5). A `vanilla-current` client never gets sent to a Fantasy (1.20.1) map. This is the core rule enforced here: **dynamic maps, standardized required runtime.**

## Tasks

### 1. Random selection in the controller

```text
candidates = maps where runtime == requester.runtime
chosen     = random(candidates)
```

### 2. Handle "no compatible maps"

If there are no compatible maps, return a clear message ("no compatible maps available") rather than sending a player to a wrong-runtime map.

### 3. Wake and transfer

Reuse the Step 10 portal flow: wake the chosen map (Step 9), then transfer the player.

## Acceptance criteria

```text
[ ] random map is always compatible with the requester's runtime
[ ] no compatible maps → clear, graceful message
[ ] chosen map is woken and player transferred
[ ] selection is reproducible/observable for debugging
```

## Next step

[Step 13 — Fantasy Forge runtime + Ambassador + ProxyCompatibleForge](step-13-fantasy-forge.md)