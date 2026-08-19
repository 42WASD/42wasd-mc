# Step 8 — World Controller

The **World Controller** is the service that decides which backend hosts a given logical map/world, and how requests are routed and woken up. It is the heart of the "dynamic" part of the architecture.

## Goal

A central controller that knows the mapping of **map → backend** and **backend → runtime**, answers "where is map X", and triggers a wake when a map isn't running.

## Responsibilities

- Maintain the registry of **runtime classes** (`vanilla-current`, `backrooms-current`, `fantasy-1.20.1-forge`, `experimental-*`).
- Map each **map/world** to a runtime and to the backend currently hosting it.
- Answer routing requests: "where does a player for map X go?"
- Trigger **wake** of a scaled-to-zero backend (Step 9) when someone requests an asleep map.
- Report status so the proxy / TAB can show exact presence.

## Core data model (sketch)

```text
RuntimeDefinition { runtime_id, image, protocol_version, mods, ... }
MapInstance       { map_id, runtime_id, world, host_backend, state (sleeping|running|...) }
```

## Tasks

### 1. Define the controller as a service

A small service (Go/Java/Python) in `minecraft-system` with:
- an internal REST/gRPC API,
- a registry database (CockroachDB or a simple store),
- an interface to the orchestrator to start/stop backend pods.

### 2. Implement routing resolution

Given a map request, return the backend host + runtime, or signal "wake required".

### 3. Wire into the proxy

The `/join` logic (Step 7) and portal logic (Step 10) consult the controller instead of a static table.

## Acceptance criteria

```text
[ ] controller knows each map's runtime and host backend
[ ] routing query returns host or wake signal
[ ] status reflects sleeping/running/running per backend
[ ] controller is the single source of truth for map→runtime
```

## Next step

[Step 9 — Scale-to-zero map (Persistent StatefulSet)](step-09-scale-to-zero.md)