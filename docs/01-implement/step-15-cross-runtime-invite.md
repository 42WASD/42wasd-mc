# Step 15 — Cross-runtime invite

Let a player invite a friend to a map even when they run a **different runtime** — because "community map may be dynamic; the required client runtime must be standardized."

## Goal

An invite can target a map whose runtime differs from the inviter's current runtime, and the recipient can only join if their runtime is compatible.

## Concept

- **Invite policy** (Step 6) governs *who may join* (friends-only, etc.).
- **Runtime compatibility** (Step 12) governs *whether a given player can physically join* that map.
- A cross-runtime invite checks compatibility before joining; if incompatible, it says so clearly.

## Tasks

### 1. Extend invites with a target map + runtime

An invite now carries the target **map** (and thus its runtime class), not just "join my party."

### 2. Enforce runtime on acceptance

When a recipient accepts, the controller verifies the recipient's client runtime matches the target map's runtime. If not:

- block with a clear message ("you need the fantasy runtime to join"), and
- optionally suggest the Modrinth project (Step 14) to install.

### 3. Reuse the wake/transfer flow

Once accepted and runtime-verified, wake (Step 9) and transfer (Step 10).

## Acceptance criteria

```text
[ ] a fantasy player can invite a vanilla player to a fantasy map
[ ] vanilla recipient is correctly rejected/advised on runtime
[ ] a compatible recipient is transferred via the normal flow
[ ] invite policy and runtime compatibility are evaluated separately
```

## Next step

[Step 16 — mc-router edge wake](step-16-mc-router.md)