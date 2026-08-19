# Step 7 — Second static backend + /join

Prove cross-server movement without any dynamic spawning: add a second static backend and a way to move between them.

## Goal

A player can move from the lobby to a second static backend and back, via a repeatable mechanism.

## Tasks

### 1. Add a second static backend

Deploy a second static Paper server (for example `survival-main`) the same way as the lobby, on a ClusterIP behind the proxy.

```toml
[servers]
lobby = "lobby.minecraft.svc.cluster.local:25565"
survival-main = "survival-main.minecraft.svc.cluster.local:25565"
```

### 2. Add the `/join` command

A Velocity plugin (or a lightweight custom module) exposing `/join <backend>` that:

1. Validates the target backend exists and is registered.
2. Performs a **transfer** of the player from lobby → `survival-main`.
3. Keeps the player's identity intact (modern forwarding already in place).

```java
// pseudocode
if (args.length < 1) { error("Usage: /join <server>"); return; }
ServerInfo target = server.getServer(args[0]).orElseThrow(...);
player.createConnectionRequest(target).fireAndForget();
```

### 3. Handle the unknown-server case

If the target backend is not registered (or down), fail gracefully with a message instead of dropping the player.

## Acceptance criteria

```text
[ ] `/join survival-main` moves the player to the second backend
[ ] player can `/join lobby` to return
[ ] unknown backend yields a clear error, player is not dropped
[ ] identity and presence carry across the transfer
```

## What this proves

Movement between backends works and is safe. The rest of the guide extends this same transfer mechanism to **dynamic** backends that may not exist yet (wake → transfer in Step 10).

## Next step

[Step 8 — World Controller](step-08-world-controller.md)