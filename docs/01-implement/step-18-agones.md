# Step 18 — Agones ephemeral fleet (optional)

For cases where you want short-lived, scalable, per-match sessions, you can add **Agones** to run ephemeral game-server fleets instead of only persistent StatefulSets.

This step is **optional** — the persistent scale-to-zero (Step 9) covers most needs.

## Goal

Agones runs a fleet of ephemeral servers that are created on demand and destroyed when the match ends, integrated with the existing transfer flow.

## Why/when to use Agones

- Temporary sessions (arena, event maps) where persistence doesn't matter.
- Fleet that autoscales independently of persistent maps.

## Tasks

### 1. Install Agones

Install the Agones controller into the cluster.

### 2. Define a fleet

A Fleet CR with the game-server template (backend image, runtime class, resource limits).

### 3. Integrate with the controller

- Allocate a `GameServer` on demand.
- Report the allocated server's address/port as a backend target.
- Tear down and return the GameServer to the pool when the session ends.

## Acceptance criteria

```text
[ ] Agones Fleet / GameServer resources create an ephemeral backend
[ ] a new session is routed to an allocated GameServer
[ ] lifecycle (allocate → play → shutdown) works through the controller
[ ] runtime compatibility rules still apply (same as persistent backends)
```

## Next step

[Step 19 — AI proximity bot](step-19-ai-proximity.md)