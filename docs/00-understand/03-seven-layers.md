# The seven layers

Each layer answers one question. Keep them separate.

| # | Layer | Question it answers | Recommended |
|---|---|---|---|
| 1 | ENTRY | How does the player reach the network? | `mc-router` (optional) → Velocity |
| 2 | PROXY | Which backend should this player use? | **Velocity** |
| 3 | SOCIAL | Who is friends with whom, who invited whom? | **Nakama** |
| 4 | WORLD CONTROL | Which world exists, and is it ready? | **custom World Controller** |
| 5 | GAME SERVERS | Where does the simulation run? | `itzg/minecraft-server` |
| 6 | PROTOCOL | Can these protocol versions talk? | ViaVersion + ViaBackwards |
| 7 | CLIENT RUNTIME | Does the player have the right game/loader/mods? | Modrinth Server Projects (+ packwiz) |

## Layer details

### 1. ENTRY
`mc-router` is useful when players come in via different hostnames (`play`, `survival`, `map-abc`) or you want edge-triggered wake. If everyone enters one address and all routing happens post-login, `mc-router` is optional.

### 2. PROXY
Velocity handles Mojang auth, backend switching, proxy commands, TAB, protocol translation, Forge compatibility, and the custom NetworkBridge plugin. It is chosen for its plugin ecosystem.

### 3. SOCIAL
Nakama owns identity mapping, friends, parties, invites, presence, notifications, and pending cross-runtime joins. A proxy plugin should not become the authoritative social database.

### 4. WORLD CONTROL
A small service owning the map catalog, runtime compatibility, lifecycle (scale 0→1), readiness, reservations, random selection, route registration, and idle scale-down. It gets narrowly scoped Kubernetes permissions.

### 5. GAME SERVERS
`itzg/minecraft-server`: Paper for vanilla-compatible modes, Forge for fantasy, StatefulSet + PVC for durable worlds, Agones only for disposable session worlds.

### 6. PROTOCOL
ViaVersion (newer→older), ViaBackwards (older→newer). Only for runtime classes designed to tolerate translation. Never a substitute for mod testing.

### 7. CLIENT RUNTIME
Modrinth Server Projects for public onboarding; packwiz as optional Git/CI source. Owns MC version, loader, mods, versions, configs, resource packs, runtime updates.