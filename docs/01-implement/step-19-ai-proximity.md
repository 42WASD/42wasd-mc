# Step 19 — AI proximity bot

Optional capstone: a lightweight "AI" presence that responds when a player is near (proximity-based), demonstrating the evented, controller-driven nature of the network.

## Goal

A bot that is aware of player proximity (its position vs. players) and triggers a behavior when someone comes near — proving the presence/proximity infrastructure works end-to-end.

## Tasks

### 1. Emit proximity events

- A backend plugin detects players within range of the bot's position and emits a proximity event (who is near, their identity).

### 2. Hook into the controller/event system

- The proximity event flows to a handler (controller / a small service) that decides the bot's behavior.

### 3. React

- The bot performs an action (e.g., a message, a portal trigger, a teleport, a map wake) when triggered. Demonstrate reusing the same identity/presence data used everywhere.

## Acceptance criteria

```text
[ ] bot knows when a player enters its proximity
[ ] the event triggers a defined response
[ ] response can reuse network primitives (presence, transfer, wake)
[ ] behavior is observable/debuggable
```

## You're done!

Reaching this step means you have a functioning dynamic, runtime-aware, scale-to-zero Minecraft network:

- **Identity** — stable, proxied forwarding (Steps 1-2).
- **Presence** — exact map presence via TAB (Steps 3, 11).
- **Protocol/runtime** — version and modded runtime classes (Steps 4, 13-14).
- **Social** — friends/parties/invites on Nakama (Steps 5-6, 15).
- **Dynamic** — World Controller + scale-to-zero + portal wake/transfer + random maps (Steps 8-12).
- **Edge/ops** — mc-router edge wake, map upload, optional Agones (Steps 16-18).

See [02-reference](../02-reference/index.md) for the detailed contract/schema references, and [03-operations](../03-operations/index.md) for running and maintaining it.