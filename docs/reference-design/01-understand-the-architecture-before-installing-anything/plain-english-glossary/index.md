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
Your small control-plane service that reads map definitions, decides *which* instance should run, and turns player routing requests into safe Kubernetes lifecycle operations. It is the **decision-maker**, not the compute layer:
- It reads a `MapDefinition` and, on demand, drives the underlying workload — it scales an **OpenKruiseGame `GameServerSet`** (the thing that actually runs the Minecraft server) 0→1, waits for readiness, registers a route, and reserves capacity.
- It owns **traffic policy**: it tells the proxy/NetworkBridge which backend a player/party should be routed to. It does not tunnel the bytes itself; Velocity and mc-router carry the actual player traffic.
- It does **not** host the Minecraft server process (OKG/GameServerSet does) and it is **not** the proxy (Velocity is).

So: World Controller = reads map definition + decides + orchestrates lifecycle + policy for traffic. OKG = runs/sleeps the actual server pod. Velocity/mc-router = carry the traffic.

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

> **Old modded world + newer client?** ViaVersion/ViaBackwards translate the
> *network protocol* (packets), so they work on vanilla-like servers and can
> bridge version gaps between the wire protocol of client and server. They
> **cannot** supply missing *client mods/registry content*. If the older world
> is modded (Forge/Fabric with custom blocks, entities, registries), a newer
> client cannot be made compatible by protocol translation alone — the client
> would be missing the mods. In that case **AstralRinth / Modrinth Server
> Project** takes over: the launcher provisions the *exact* required
> runtime (Minecraft version + loader + mods) so the client matches the
> server's registry. Protocol translation is only usable for runtimes that
> tolerate version translation; modded runtimes use launcher-matched runtimes.

## Resource pack
Assets that Minecraft servers can request clients to download, such as textures, sounds, fonts, and models. It is not equivalent to Java mods.

## Modpack
A defined set of Minecraft loader/mod/config dependencies installed before game startup.

## Pending invite
A durable short-lived record that survives a launcher restart and tells the network where the player intended to go when they reconnect.

> **Does it expire? Yes.** A pending invite is *short-lived*: it carries an
> `expires_at` (a few minutes to a few hours) and becomes `EXPIRED` after
> that. It is **not** kept forever — the invite target (a world, a party, a
> friend's location) becomes stale quickly, and a stale invite would route a
> player to a world that is gone or has no reservation. On expiry the record
> is kept (so the player sees "your invite expired") but no longer routes
> anyone. This matches the invite-policy: `PENDING → ACCEPTED →
> CONSUMED`, or `EXPIRED`/`DECLINED`.

## Velocity
The default modern Minecraft proxy used here. It is the single public entry point that routes players to backend worlds and enforces forwarding identity.

> **Language & scale:** Velocity is written in **Java**. It is designed for
> throughput: a single instance comfortably handles **1000+ concurrent
> players**. The rule of thumb is roughly **512MB of heap per 500 players**
> (≈1GB heap for 1000), and the container should be sized at ~2× heap + 2GB
> (≈4GB total for 1000). It routes packets rather than simulating worlds, so
> CPU/RAM are modest — the heavy spend is the backend Minecraft servers, not
> the proxy.

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

> **What versions they cover (2026 audit).** They sit on the proxy (Velocity)
> and translate the network protocol, so the exact supported range is defined
> by the Via project build, not by the server. As of the 2026 audit:
> - **ViaVersion** (newer client → older server): a server on, say, 1.20 can
>   accept clients from ~1.9 up to the current release.
> - **ViaBackwards** (older client → newer server): runs on servers 1.10–
>   latest and accepts clients down to ~1.9. Clients 1.8 and older need
>   **ViaRewind** (1.7–1.12 rewind).
>
> Always check viaversion.com / the Hangar page for the exact current ranges —
> they change with each Minecraft release. And protocol compatibility is not
> mod compatibility (see the modded-world note under *Protocol translation*).

## ViaLite
Gate's built-in protocol-translation path (Gate's analogue of ViaVersion/ViaBackwards). Referenced when comparing Gate to Velocity; the selected default here is Velocity + ViaVersion/ViaBackwards.

## Ambassador / ProxyCompatibleForge
Paper's documented way to make Velocity + Forge 1.13–1.20.1 work together (modern forwarding compatible with Forge).

> **What they actually are and when they apply.**
> - **Ambassador** is a **Velocity proxy plugin** that solves a specific
>   problem: Forge servers on **1.13–1.20.1** run their mod-negotiation during
>   the *login* phase, which Velocity cannot relay on its own. Ambassador
>   relays that Forge login negotiation between the backend and the client so
>   a modern Forge server can sit behind Velocity. **It only applies to
>   Forge 1.13–1.20.1** — Velocity has *built-in* Forge support for versions
>   **above 1.20.2**, so Ambassador is not used for newer Minecraft (26.x
>   needs no Ambassador).
> - **Proxy-Compatible-Forge (PCF)** is a **server-side Forge mod** that
>   implements Velocity's **modern player-info forwarding** (the secure
>   UUID/IP handoff) on Forge, so modded servers work with Velocity's
>   authenticated forwarding. Paper/Spigot support this natively; Forge needs
>   PCF. It is server-side only (players install nothing).
>
> Together: Ambassador (proxy) makes Forge 1.13–1.20.1 *connect*, and PCF
> (server) makes the connection *secure with real forwarding*. For newer
> Forge/NeoForge (1.20.2+), Ambassador is unnecessary but PCF (or native
> forwarding) is still relevant.

## mc-router
A hostname-based edge router that can route and optionally wake a sleeping world on the hostname request. It is a trigger, not the lifecycle authority.

## itzg/minecraft-server
The standard Docker image for running any Minecraft server type/version/modpack. itzg/mc-proxy is its Velocity proxy variant; itzg/mc-monitor probes Minecraft status and exports metrics.

## Modrinth Server Projects
A Modrinth feature that lets a server publish "the required content to play here", so the launcher can install it and launch directly.

## AstralRinth
A fork of the Modrinth launcher app that also supports offline/cracked accounts. This design tracks the fork under our own GitHub org (`42WASD/AstralRinth`) so we pin a known-good build rather than a floating upstream.

> **"Join" installs-or-finds-or-updates, then launches.** Because AstralRinth
> is a Modrinth App fork, it manages *instances* (per-runtime installs) and
> reuses them: it does **not** re-create a runtime every time.
> - If the required runtime is **already installed**, it launches it directly.
> - If installed but **out of date**, it updates it in place (Modrinth App
>   keeps installed mods/packs up to date per instance).
> - If **not installed**, it installs it (Minecraft version + loader + mods)
>   and launches.
>
> So when a player clicks **Join**, NetworkBridge resolves the runtime, and the
> launcher does "install / update / launch existing" as needed — the exact
> "auto-load the modded world" behavior the design is built around.

## packwiz
A Git-friendly tool for defining and updating a modpack that server and launcher both consume.

> **How packwiz relates to the rest.** packwiz is the **authoring/source**
> layer for a runtime's client/server mod set: you keep the mod list as
> Git-friendly TOML, CI can validate it, and you export to a **Modrinth pack**
> that the launcher installs. It pairs with:
> - **Runtime definition** — the *mod set* (the pack) is part of a runtime
>   class; the runtime revision (r1, r2…) is bumped when the pack changes.
> - **Modrinth Server Projects** — packwiz exports the `.mrpack` that
>   Modrinth/AstralRinth installs on the client.
> - **Map definition** — a map points at a *runtime*, and the runtime pins the
>   pack version. The map itself usually doesn't carry mod versions; the
>   runtime/pack does. (A map may pin a *world/content* revision separately,
>   but its client-required mods come from the runtime's pack.)
>
> So: **runtime definition pins the pack/revision**, **packwiz authors the
> pack**, **Modrinth Server Project distributes it to the launcher**, and
> **map definitions select which runtime a map needs.**

## KEDA
A Kubernetes event-driven autoscaler that can scale a workload from 0 to 1 (and back). Here it triggers the GameServerSet 0↔1 transition.

## Velero
A Kubernetes backup/restore tool that snapshots PVCs (including worlds) on a schedule and can restore them elsewhere.

---
