# Step 13 — Fantasy Forge runtime + Ambassador + ProxyCompatibleForge

Introduce a second, incompatible runtime: **Fantasy (1.20.1 Forge)**. This is where the network must handle a *different Minecraft version + modded* backend, alongside the vanilla runtimes.

## Goal

A Forge-based map (`fantasy-1.20.1-forge`) runs as a backend and is reachable through the same proxy, using **ProxyCompatibleForge** and the **Ambassador** pattern so modern forwarding still works.

## Background

Forge can conflict with modern (Velocity) forwarding. **ProxyCompatibleForge** is the mechanism that lets a Forge backend work behind Velocity; the **Ambassador** is a bridge that keeps the proxy protocol intact. This is the trickiest runtime integration in the whole guide.

## Tasks

### 1. Stand up the Forge runtime

- Deploy a Forge 1.20.1 backend (image `itzg/minecraft-server` with the appropriate Forge/version env), as a distinct runtime class.
- It must register as `fantasy-1.20.1-forge` in the controller (Step 8).

### 2. Apply ProxyCompatibleForge

- Configure the Forge server to be proxy-compatible so Velocity forwarding works.
- Follow the vendor's recommended config for ProxyCompatibleForge with Velocity.

### 3. Add the Ambassador

- Place the Ambassador so the proxy→forge connection carries the correct forwarding/protocol metadata.
- Verify the backend appears with the right runtime and accepts transfers.

### 4. Register in the controller

- Ensure the controller routes only `fantasy-1.20.1-forge`-compatible clients to this backend (enforced from Step 12).

## Acceptance criteria

```text
[ ] Forge 1.20.1 backend runs behind the proxy
[ ] ProxyCompatibleForge config applied correctly
[ ] Ambassador handles the proxy protocol handshake
[ ] forwarding identity survives to the Forge backend
[ ] only `fantasy-1.20.1-forge` clients can be routed here
[ ] it coexists with the vanilla runtimes
```

## Next step

[Step 14 — Modrinth Server Project](step-14-modrinth.md)