# Plain-English glossary

## Proxy
A server that players connect to first and that can route one player connection among multiple Minecraft backend servers.

## Backend
The actual Paper/Forge/Fabric/NeoForge Minecraft server process running a world or mode.

## Runtime class
A compatibility contract describing the Minecraft version, loader, required client mods, and server capabilities a map is allowed to assume.

## Map definition
Metadata describing a playable map: runtime class, world source, tags, capacity, persistence, owner, and routing policy.

## Map instance
A running or sleeping concrete backend created from a map definition.

## World Controller
Your small control-plane service that turns player routing requests into safe Kubernetes lifecycle operations.

## OpenKruiseGame (OKG)
A CNCF-incubated, actively maintained Kubernetes workload specialized for stateful game servers (a sub-project of OpenKruise).

## GameServerSet
The OKG workload with stable per-server identity; supports in-place update, per-server `opsState` protection, PVC-backed worlds (VolumeClaimTemplates), and scale-to-zero.

## GameServer
The per-server OKG resource; represents a single game-server instance and its lifecycle/O&M state.

## PVC
PersistentVolumeClaim. The persistent disk claim holding a world even while its server Pod is scaled to zero.

## Scale-to-zero
Keeping a world definition and data while running zero server Pods when nobody is using it.

## Agones Fleet
A set of game-server instances kept available for allocation.

## Allocation
Atomically selecting/reserving a game-server instance for a session.

## Presence
Live information describing whether a player is online and what they are currently doing.

## Protocol translation
Translation between Minecraft network protocol versions. It does not install missing mods.

## Resource pack
Assets that Minecraft servers can request clients to download, such as textures, sounds, fonts, and models. It is not equivalent to Java mods.

## Modpack
A defined set of Minecraft loader/mod/config dependencies installed before game startup.

## Pending invite
A durable short-lived record that survives a launcher restart and tells the network where the player intended to go when they reconnect.

## Velocity
The default modern Minecraft proxy used here. It is the single public entry point that routes players to backend worlds and enforces forwarding identity.

## NetworkBridge
Your small custom Velocity plugin that binds the Minecraft UUID/name to the Nakama account and triggers World Controller routing (/worlds, /join, /invite).

## Auth gate
The stage every player passes through after joining the network but before reaching a real world. It requires the player to sign in (Discord/Google OAuth → Nakama) and links their Minecraft identity to a verified Nakama account before allowing transfer onward. It is what makes an offline/cracked-capable network safe. Sign-in here is **one-time**: the Nakama session (with a refresh token) persists across launcher restarts, so switching runtimes does not force a re-login.

## Nakama
An open-source game backend that owns accounts, sessions, friends, parties, invites, presence and chat. Here it is the OAuth-first identity anchor.

## CockroachDB
The production database Nakama uses for accounts and social state.

## TAB
A plugin that shows a sidebar/tab list with player info (here: global presence and current world), powered by MiniPlaceholders.

## ViaVersion / ViaBackwards
Protocol-translation plugins that let newer clients connect to a server running an older Minecraft version (ViaVersion) or let older clients join a newer server (ViaBackwards). They do not install missing mods.

## ViaLite
Gate's built-in protocol-translation path (Gate's analogue of ViaVersion/ViaBackwards). Referenced when comparing Gate to Velocity; the selected default here is Velocity + ViaVersion/ViaBackwards.

## Ambassador / ProxyCompatibleForge
Paper's documented way to make Velocity + Forge 1.13–1.20.1 work together (modern forwarding compatible with Forge).

## mc-router
A hostname-based edge router that can route and optionally wake a sleeping world on the hostname request. It is a trigger, not the lifecycle authority.

## itzg/minecraft-server
The standard Docker image for running any Minecraft server type/version/modpack. itzg/mc-proxy is its Velocity proxy variant; itzg/mc-monitor probes Minecraft status and exports metrics.

## Modrinth Server Projects
A Modrinth feature that lets a server publish "the required content to play here", so the launcher can install it and launch directly.

## AstralRinth
A fork of the Modrinth launcher app that also supports offline/cracked accounts. This design tracks the fork under our own GitHub org (`42WASD/AstralRinth`) so we pin a known-good build rather than a floating upstream.

## packwiz
A Git-friendly tool for defining and updating a modpack that server and launcher both consume.

## KEDA
A Kubernetes event-driven autoscaler that can scale a workload from 0 to 1 (and back). Here it triggers the GameServerSet 0↔1 transition.

## Velero
A Kubernetes backup/restore tool that snapshots PVCs (including worlds) on a schedule and can restore them elsewhere.

---
