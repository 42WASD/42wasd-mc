# Random map scoring

How the "random compatible map" flow (Step 12) selects a map for a player.

## Invariants

- The chosen map's `runtimeId` must be in the requester's **compatible runtimes**.
- The choice is only among **available** maps (not error/starting, or at least a known-good state).
- Never pick a map that would require the player to install a different runtime than they currently have.

## Selection algorithm

```text
function pickRandom(requesterRuntime):
  compatible = allMaps where map.runtimeId.compatibleClients contains requesterRuntime
  if compatible is empty:
      return NO_COMPATIBLE_MAPS
  # optional: weight by score
  return weightedRandom(compatible)
```

## Weighting (optional)

You may weight selection by factors such as:

- freshness (recently-uploaded maps) — see [map upload](../01-implement/step-17-map-upload.md)
- player count (avoid overloaded backends)
- manual boost/pin for certain maps

Weighting must **not** violate the runtime invariant above.

## Failure handling

- `NO_COMPATIBLE_MAPS` → tell the player clearly, don't send them to a wrong-runtime map.
- Candidate woken but fails → return to lobby (reuse Step 10 failure path).

## See also

- [Step 12 — Random compatible map](../01-implement/step-12-random-map.md)
- [RuntimeDefinition](runtime-definition.md)
- [MapInstance](map-instance.md)