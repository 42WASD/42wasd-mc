# Step 17 — Community map upload pipeline

Let the community upload maps that are validated, classified into a runtime class, and then available to players through the random/portal system.

## Goal

A safe, automated path from a community-submitted map → validated → assigned a runtime → available on the dynamic network.

## Tasks

### 1. Accept uploads

- A controlled place to accept map uploads (a web/API endpoint, not a raw file share).
- Capture map name, author, and the claimed runtime requirement.

### 2. Validate the map

- Verify it is a valid Minecraft map/world.
- **Classify its runtime** — determine which runtime class (`vanilla-current`, etc.) it needs. This is the "required client runtime standardized" step: the upload declares or is validated into a runtime.
- Reject maps whose runtime is incompatible/unknown or that fail validation.

### 3. Register in the controller

- On success, register the map in the World Controller (Step 8) with its runtime.
- Then it's selectable by random-map (Step 12), portals (Step 10), and invites (Step 15).

## Acceptance criteria

```text
[ ] uploads are validated before acceptance
[ ] each map is assigned a verified runtime class
[ ] validated maps become available through the dynamic flows
[ ] invalid/incompatible maps are rejected with a clear reason
[ ] the required runtime is standardized, not per-map custom
```

## Next step

[Step 18 — Agones ephemeral fleet (optional)](step-18-agones.md)