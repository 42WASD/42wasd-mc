# Step 3 — TAB

Add TAB (v6.x) as the network-wide presence layer so players can see server/backend context everywhere, and later steps (exact map presence, cross-server presence) build on it.

## Goal

TAB is running network-wide, showing which server a player is on, with a consistent header/footer across all backends.

## Tasks

### 1. Add the TAB plugin to every backend

For a Paper backend, install `TAB` v6.1.2 (Velocity-compatible) into `plugins/`.

With `itzg/minecraft-server`, drop the jar into a plugins volume, or use the modpack/plugin manager if enabled.

### 2. Configure TAB for network context

Define a placeholder that shows the current server:

```yaml
tablist-name-formatting:
  - condition: "placeholder %player_server% is lobby"
    output: "&7[Lobby] &f%player_name%"
  - condition: "%player_server% equals backrooms-001"
    output: "&5[Backrooms] &f%player_name%"
  - output: "&8[%player_server%] &f%player_name%"
```

### 3. Verify presence propagation

Confirm that players on different backends see each other and their server labels correctly in the tab list.

## Acceptance criteria

```text
[ ] TAB v6 is installed on all backends
[ ] tab list shows server label per player
[ ] header/footer configured network-wide
[ ] no bungeecord-guess / unknown-server labels for known backends
```

## Next step

[Step 4 — ViaVersion / ViaBackwards](step-04-protocol.md)