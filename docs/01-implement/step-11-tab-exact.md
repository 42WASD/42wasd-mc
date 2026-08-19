# Step 11 — Exact map presence + TAB

Make presence **exact**: the tab list (via TAB) reports the exact **map/world** a player is on (not just the backend), and this is driven by the controller, not guessed.

## Goal

The tab list shows, for each player, the exact map they're in, updated as they move between dynamic backends — surfaced by the controller's running status (Step 8).

## Tasks

1. **Push exact map presence** — the controller reports each backend's current map, and the current running backends, to TAB / a presence provider.

2. **Backend-independent display** — the presence is about the *map*, so players on scaled-up/down backends still see the same map label while the backend name may differ.

3. **Update on the fly** — as backends wake/sleep (Step 9) and players transfer (Step 10), presence updates without a refresh.

## Acceptance criteria

```text
[ ] tab list shows exact map name per player
[ ] presence updates automatically on transfer/wake/sleep
[ ] display is stable across backend wake/sleep cycles
[ ] no "guessed" server labels remaining for dynamic maps
```

## Ties everything together

This step turns the static TAB of Step 3 into a dynamic, controller-driven presence system.

## Next step

[Step 12 — Random compatible map](step-12-random-map.md)