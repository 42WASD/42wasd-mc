# Verified Dynamic Minecraft Network / Runtime Architecture — Explained Edition

**Audit date:** 2026-08-19  
**Purpose:** define a mature, usable, Kubernetes-first architecture for a Minecraft network with dynamic worlds, community maps, parties/invites, world-aware TAB information, random “glitch” routing, modded fantasy runtimes, scale-to-zero, and the smoothest practical client onboarding.

> **Important scope note:** This is a systems-architecture and implementation guide. It deliberately separates **network routing**, **game/world lifecycle**, **social state**, **Minecraft protocol compatibility**, and **client mod/runtime distribution**. No single proxy solves all five problems, and treating them as one problem creates a fragile design.

---

# Part I — Understand the architecture before installing anything

## 0. The one-sentence idea

Build a Minecraft network where **Velocity is the stable public proxy**, a small **World Controller** owns dynamic world lifecycle in Kubernetes, **Nakama** owns friends/parties/invites/presence, **TAB** renders global player information, **mc-router** optionally wakes hostname-addressed sleeping servers, and **Modrinth Server Projects** installs the correct modded runtime when a player cannot enter a world with their currently running client.

The mental model is:

```text
                         ┌──────────────────────────────┐
                         │       PLAYER / LAUNCHER      │
                         │ Vanilla client or Modrinth   │
                         └───────────────┬──────────────┘
                                         │
                                         ▼
                              ┌─────────────────────┐
                              │     mc-router       │
                              │ optional edge/wake  │
                              └──────────┬──────────┘
                                         │
                                         ▼
                              ┌─────────────────────┐
                              │     VELOCITY        │
                              │ public MC endpoint  │
                              └──────────┬──────────┘
                                         │
          ┌──────────────────────────────┼──────────────────────────────┐
          │                              │                              │
          ▼                              ▼                              ▼
 ┌────────────────┐             ┌────────────────┐             ┌────────────────┐
 │ Lobby / Paper  │             │ Vanilla / Map  │             │ Fantasy Forge  │
 │ always ready   │             │ StatefulSets   │             │ 1.20.1 runtime │
 └────────────────┘             └────────────────┘             └────────────────┘

Velocity plugins / services
    │
    ├── TAB
    ├── ViaVersion + ViaBackwards
    ├── Ambassador (for Forge 1.13–1.20.1 backends)
    └── NetworkBridge (your small custom plugin)
             │
             ├───────────────► World Controller ─────► Kubernetes API
             │                         │
             │                         ├── wake / sleep StatefulSets
             │                         ├── wait for readiness
             │                         ├── register/unregister routes
             │                         └── random-map selection
             │
             └───────────────► Nakama
                                       │
                                       ├── friends
                                       ├── parties
                                       ├── invites
                                       ├── presence/status
                                       └── pending cross-runtime joins
```

The crucial rule is:

```text
Proxy compatibility != mod compatibility
Protocol translation != mod installation
Server lifecycle != social state
World routing != client runtime switching
```

---

# 1. Why the tempting “one tool solves everything” design is wrong

## Problem 1 — A proxy is not a world orchestrator

Velocity and Gate can route a connected player to a backend, but they are not by themselves a Kubernetes lifecycle controller.

A dynamic world requires:

```text
desired world
    ↓
is an instance already running?
    ↓
if not: start it
    ↓
wait until Minecraft is actually READY
    ↓
register route
    ↓
reserve capacity
    ↓
transfer player / party
```

A proxy should not be given unrestricted Kubernetes permissions merely because it can issue a `/server` command.

The better separation is:

```text
Velocity NetworkBridge
      ↓
World Controller API
      ↓
narrow Kubernetes RBAC
```

---

## Problem 2 — Minecraft protocol compatibility is not mod compatibility

A protocol translator such as ViaVersion/ViaBackwards, or Gate's ViaLite integration, can translate **Minecraft network protocol versions**.

It cannot invent missing client code.

This may be possible:

```text
newer Java client
    ↓
ViaVersion
    ↓
older Paper backend
```

This is fundamentally different:

```text
vanilla client
    ↓
proxy
    ↓
Forge server requiring MineColonies + Ice and Fire
```

The second case requires the correct loader/mod set on the client.

If a mod adds blocks, entities, registries, screens, packet types, recipes, animations, or required client code, a proxy cannot synthesize the missing implementation.

---

## Problem 3 — Arbitrary community modpacks destroy seamless switching

Imagine allowing every map author to choose anything:

```text
Map A -> 1.21.x Paper
Map B -> 1.20.1 Forge + 145 mods
Map C -> 1.21.x NeoForge + 80 different mods
Map D -> 1.19.2 Fabric
Map E -> another incompatible Forge registry
```

A player already inside Minecraft cannot continuously hot-replace the loader, game version, and Java classpath.

Therefore community content should target **runtime classes**.

Example:

```text
vanilla-current
backrooms-current
fantasy-1.20.1-forge
experimental-horror-1
```

A community creator chooses a runtime class and supplies compatible world/content data.

This is the single biggest product decision that makes the rest of the architecture tractable.

---

## Problem 4 — A global TAB list is not automatically a global world database

Velocity knows which **backend server** a player is connected to.

It does not necessarily know:

```text
map_id
dimension
exact world name
party
current activity
runtime class
```

That information must be reported from the backend or maintained by the network control plane.

The correct flow is:

```text
Paper/Forge bridge
    ↓ player world/dimension changed
World Controller / Nakama presence
    ↓
NetworkBridge placeholder
    ↓
TAB on Velocity
```

---

## Problem 5 — Scale-to-zero and portal switching are two different traffic paths

`mc-router` can see a new incoming connection to a hostname and can wake a Kubernetes StatefulSet before forwarding the connection.

But consider an already-connected player:

```text
Player is already connected to Velocity
    ↓
walks into portal
    ↓
Velocity wants to switch backend
```

There is no new public TCP handshake entering `mc-router`.

Therefore, for **in-game server switching**, your World Controller must perform the wake/readiness operation before Velocity transfers the player.

`mc-router` is still useful at the network edge; it is not the complete in-game world lifecycle controller.

---

# 2. The complete mental model: seven separate layers

## 2.1 ENTRY — “How does the player reach the network?”

Recommended:

```text
Internet
   ↓
mc-router (optional)
   ↓
Velocity
```

Use `mc-router` when hostname routing and edge-triggered wake-up are useful.

Examples:

```text
play.example.com
survival.example.com
map-abc.example.com
```

If every player always enters through one address and all routing happens after login, `mc-router` is optional.

---

## 2.2 PROXY — “Which backend should this connected player use?”

Recommended default: **Velocity**.

Responsibilities:

```text
Mojang authentication
backend connection switching
proxy commands
TAB plugin
ViaVersion/ViaBackwards
Forge compatibility bridge
NetworkBridge
```

Velocity is the selected default because this architecture values the **usable Minecraft plugin ecosystem** more than minimizing proxy process size.

---

## 2.3 SOCIAL — “Who is friends with whom, who invited whom, and what are they doing?”

Recommended: **Nakama**.

Responsibilities:

```text
Minecraft UUID -> network account mapping
friends
friend requests
parties
party invites
presence/status
notifications
pending cross-runtime join
optional matchmaking/listing logic
```

Do not force a Minecraft proxy plugin to become your entire social backend.

---

## 2.4 WORLD CONTROL — “Which world instance exists, and is it ready?”

Recommended: a **small custom World Controller service**.

Responsibilities:

```text
map catalog
runtime compatibility
instance lifecycle
Kubernetes scale 0 -> 1
readiness checks
capacity reservations
random-map selection
route registration
idle scale-down policy
```

This service should have narrowly scoped Kubernetes permissions.

---

## 2.5 GAME SERVERS — “Where does simulation actually run?”

Recommended container foundation:

**`itzg/minecraft-server`**

Use:

```text
Paper for vanilla-compatible modes
Forge for fantasy-1.20.1
persistent StatefulSet + PVC for durable worlds
Agones only for session-style disposable/warm-pool instances
```

---

## 2.6 PROTOCOL — “Can this Minecraft protocol version communicate?”

Recommended on Velocity:

```text
ViaVersion
ViaBackwards
```

Use protocol translation only for runtime classes designed to tolerate version translation.

Do not treat it as a substitute for mod compatibility testing.

---

## 2.7 CLIENT RUNTIME — “Does the player have the required game + loader + mods?”

Recommended public onboarding:

**Modrinth Server Projects**

Recommended pack authoring/CI option:

**packwiz**

The launcher layer owns:

```text
Minecraft version
loader
required mods
mod versions
configs
resource packs
runtime updates
```

---

# 3. Runtime classes: the rule that makes seamless UX possible

Define a small number of supported runtime contracts.

## Runtime A — `vanilla-current`

Example:

```yaml
id: vanilla-current
kind: paper
minecraft_protocol_policy: via-compatible
client_modpack_required: false
server_resource_pack: optional
community_maps_allowed: true
```

Use for:

- lobby;
- ordinary survival;
- community adventure maps;
- minigames;
- creative/build worlds;
- lightweight horror experiences.

This runtime should provide the most seamless experience.

---

## Runtime B — `backrooms-current`

Prefer a Paper/server-side implementation where possible:

```yaml
id: backrooms-current
kind: paper
client_modpack_required: false
required_resource_pack: true
community_maps_allowed: true
```

Use resource packs, server-side plugins, datapacks, custom model data, sounds, display entities, and server mechanics where possible.

Why?

Because:

```text
invite
  ↓
click Join
  ↓
transfer immediately
```

is a much better user experience than restarting Minecraft for every horror map.

---

## Runtime C — `fantasy-1.20.1-forge`

Example contract:

```yaml
id: fantasy-1.20.1-forge
kind: forge
minecraft_version: "1.20.1"
client_modpack_required: true
modpack_id: "fantasy-runtime"
proxy_compatibility: "velocity + ambassador + proxycompatibleforge"
community_maps_allowed: true
```

Possible content:

```text
MineColonies
Ice and Fire
Cataclysm
fantasy mobs
structure/worldgen mods
performance mods
```

Every map in this class uses the **same required client registry/modpack contract**.

A map author may contribute:

```text
world data
schematics
quests
scripts
server configs allowed by policy
resource packs
map metadata
```

but cannot silently add an arbitrary client-required mod.

---

## Runtime D — `experimental-*`

These are intentionally separate experiences:

```text
experimental-horror-1
experimental-tech-1
experimental-rpg-2
```

Each can have its own Modrinth Server Project.

They are allowed to require launcher restart.

Do not put them into the random instant-portal pool for clients that are not already running that runtime.

---

# 4. Proxy decision: Velocity vs Gate after the 2026-08 audit

## Selected default: Velocity

As of the audit date:

- Velocity remains actively developed.
- PaperMC's current getting-started documentation requires **Java 25**.
- The repository shows a **4.0.0** release in 2026.
- It has first-class support goals for Paper, Sponge, Fabric and Forge.
- Its surrounding plugin ecosystem makes TAB, ViaVersion, permissions, social bridges, and custom Java plugins easier to assemble.

For this project, “best” means:

```text
mature ecosystem
predictable operational model
good documentation
plugin availability
modded backend path
easy custom extension
```

That makes Velocity the better default than Gate.

---

## Where Gate is genuinely stronger

Gate is not merely “Velocity in Go.”

Gate is attractive when you prioritize:

```text
small Go-native proxy/runtime
cloud-native custom engineering
Gate SDK/API control
built-in/managed ViaLite path
built-in Gate ecosystem for Java/Bedrock translation
specific Forge FML compatibility behavior
hostname/Lite-mode reverse proxy use cases
```

Gate's current documentation says Gate classic can route backend connections through managed Via-powered translation, and its modded-server documentation explicitly covers Forge 1.13–1.20.1.

This is meaningful for your fantasy runtime because Velocity itself needs Ambassador for Forge 1.13–1.20.1.

---

## Why Gate is still not selected as the default

Your requirements are not primarily “build a proxy platform.”

They are:

```text
TAB
friends
party invites
click-to-join
portal routing
world lifecycle
community maps
modded compatibility
operational simplicity
```

Velocity's ecosystem gives you a shorter path to those product features.

Gate becomes more compelling if you later decide:

> “I want the network proxy itself to be a custom cloud-native component and I am willing to engineer more of the Minecraft product layer.”

---

## Gate does not solve incompatible mod switching

Even with Gate's managed Java-version translation:

```text
protocol translation != Forge registry equivalence
```

Switching between modded backends is only safe when the client and server-side mod/registry expectations are compatible.

Therefore the runtime-class rule remains required under Gate too.

---

# 5. The selected tool stack

| Layer | Selected tool | Why it is selected |
|---|---|---|
| Public proxy | **Velocity 4.0.0 stable line** | Mature Minecraft ecosystem; active 2026 development; strong Paper docs |
| Proxy JVM | **Java 25** | Required by current Velocity docs |
| Global TAB | **TAB 6.1.2** | Current Aug 2026 release; all-in-one; Velocity support; MiniPlaceholders integration |
| Protocol translation | **ViaVersion 5.11.0 + ViaBackwards 5.11.0** | Current Jul 2026 release line; mature protocol bridge |
| Forge 1.20.1 proxy compatibility | **Ambassador + ProxyCompatibleForge** | PaperMC's documented path for Velocity + Forge 1.13–1.20.1 and modern forwarding |
| Social/meta backend | **Nakama 3.40.0** | Mature open-source game backend; friends, parties, presence, chat, matchmaking primitives |
| Nakama production DB | **CockroachDB** | Current Nakama server config documentation treats CockroachDB as required/supported production database |
| Minecraft containers | **itzg/minecraft-server 2026.8.0 line** | Very active; supports versions/loaders/modpacks |
| Proxy container | **itzg/mc-proxy `java25` variant** | Convenient Velocity container; explicitly provides Java 25 variant |
| Edge hostname routing / external wake | **itzg/mc-router** | K8s discovery; StatefulSet scale 0↔1; webhook; metrics |
| Persistent world orchestration | **Custom World Controller + StatefulSet + PVC** | Exact fit for persistent maps, portals, invites, readiness and policy |
| Ephemeral session maps | **Agones, optional** | Mature Kubernetes game-server Fleet/Allocation model |
| Public modded onboarding | **Modrinth Server Projects** | Current 2026 flow can install required content and launch directly into the server |
| Pack source/CI | **packwiz, optional** | Git-friendly modpack definition and launcher/server update workflow |
| Dynamic infra source of truth | **Git + Kubernetes manifests** | Auditable, deterministic runtime/map definitions |

---

# 6. Why several attractive projects are not the foundation

## Shulker

Shulker is conceptually very close to this project: a Kubernetes operator for dynamic Minecraft infrastructure.

However, its public release cadence is materially less current than the components selected above.

Decision:

```text
Learn from Shulker's architecture.
Do not make the first production version depend on it.
Re-evaluate if active maintenance resumes strongly.
```

---

## CloudNet

CloudNet is a serious Minecraft-native cloud system and is actively moving in 2026.

However, its 4.0 line is still in **release-candidate** status during this audit.

It is a good alternative when you want:

```text
Minecraft-native cloud manager
templates
dynamic services
less Kubernetes-specific ownership
```

It is not selected because this project is explicitly Kubernetes-first.

---

## SLS / SLS-LITE

SLS-LITE is actively useful for a smaller single-machine network and can launch/supervise local Java servers, perform matchmaking/queues, and transfer players.

This makes it interesting for a non-Kubernetes deployment.

It is not the selected foundation because:

```text
your Kubernetes cluster already exists
you want persistent PVC-backed worlds
you want infrastructure policy / RBAC
you want scale-to-zero controlled by K8s
```

---

## AutoModpack

AutoModpack is useful in a trusted, closed modded community.

But the client already needs AutoModpack, and installing/updating executable mods from a remote server has an explicit trust/security dimension.

It also cannot make Java hot-load a new classpath without restart.

Use it only if you intentionally operate a trusted fixed modded community.

For public onboarding, Modrinth Server Projects is cleaner.

---

# 7. Social state: why Nakama belongs beside Minecraft rather than inside it

A proxy plugin can implement `/friend`, `/party`, and `/invite`.

The question is whether it should become the **authoritative database and realtime social system**.

Nakama already has the game-backend primitives:

```text
authentication identity
friends
parties
party invites
presence/status
notifications
chat
match/listing/matchmaking primitives
server runtime functions
```

Use Minecraft as one client/frontend of that social system.

---

## 7.1 Identity mapping

The canonical identity should be the authenticated Minecraft UUID.

Example:

```text
minecraft_uuid = 123e4567-e89b-12d3-a456-426614174000
       ↓
Nakama custom authentication ID
       ↓
nakama_user_id
```

Maintain a table/mapping such as:

```json
{
  "minecraft_uuid": "123e4567-e89b-12d3-a456-426614174000",
  "nakama_user_id": "....",
  "minecraft_name": "Steve"
}
```

Do not make usernames authoritative; usernames can change.

---

## 7.2 The Minecraft client does not need a Nakama SDK

The flow can remain fully server-side:

```text
Minecraft client
    ↓
Velocity NetworkBridge
    ↓
Nakama HTTP / realtime API
```

The proxy acts as a trusted broker.

That means ordinary vanilla clients do not install anything merely to use:

```text
/friend
/party
/invite
/join
/worlds
/random
```

---

## 7.3 Presence model

A useful status object:

```json
{
  "runtime_id": "backrooms-current",
  "map_id": "backrooms-level-0-a17",
  "backend_id": "map-a17",
  "dimension": "minecraft:overworld",
  "activity": "exploring",
  "joinable": true,
  "party_id": "optional"
}
```

This one object can power:

```text
TAB
/join <friend>
friend menu
invite routing
party-follow
web status page
```

---

# 8. Dynamic world lifecycle

Use two different lifecycle types.

## 8.1 Persistent worlds

Examples:

```text
main survival
player-owned world
long-running community world
MineColonies colony world
```

Use:

```text
StatefulSet
+ stable Service
+ PVC
+ replicas 0 or 1
```

Lifecycle:

```text
SLEEPING
   ↓ request
STARTING
   ↓ pod Ready + Minecraft ping Ready
READY
   ↓ reservation
JOINABLE
   ↓ no players / idle timeout
DRAINING
   ↓ save + stop
SLEEPING
```

The PVC remains while replicas become zero.

---

## 8.2 Ephemeral session worlds

Examples:

```text
Backrooms run generated from immutable template
temporary minigame
one-session dungeon
short-lived challenge
```

Use Agones when you genuinely want:

```text
warm pool
atomic allocation
session lifecycle
autoscaling fleet
discard instance afterward
```

Do not force long-lived player worlds into Agones merely because Agones is a game-server operator.

---

# 9. End-to-end user experiences

## Example A — Join a vanilla friend instantly

```text
Steve is in lobby.
Alex is in vanilla survival.
Steve types /join Alex.

NetworkBridge
    ↓ resolves Alex presence in Nakama
World Controller
    ↓ confirms world is ready
Velocity
    ↓ transfers Steve
Backend
    ↓ spawns Steve according to join policy
```

No restart.

---

## Example B — Friend is in a sleeping community map

```text
Alex invites Steve
    ↓
Nakama records invite
    ↓
Steve accepts
    ↓
World Controller sees replicas=0
    ↓
scale StatefulSet 0 -> 1
    ↓
wait for K8s Ready
    ↓
wait for Minecraft protocol readiness
    ↓
register backend
    ↓
Velocity transfers Steve
```

The player may remain in lobby with:

```text
"Starting Floating Kingdom…"
```

Do not transfer to a TCP port merely because the Pod exists.

---

## Example C — “Glitch me somewhere”

```text
Player enters unstable portal
    ↓
backend sends route request
    ↓
World Controller filters map catalog:
      runtime compatible?
      map enabled?
      enough capacity?
      party allowed?
      recently visited?
    ↓
weighted random selection
    ↓
wake / allocate
    ↓
play glitch transition
    ↓
transfer
```

For a party, reserve capacity for the entire party before routing the leader.

---

## Example D — Invite crosses into the fantasy Forge runtime

Steve is currently running the vanilla runtime.

Alex is in:

```text
fantasy-1.20.1-forge
```

Flow:

```text
Alex -> /invite Steve
        ↓
Nakama stores pending invite:
  target_runtime=fantasy-1.20.1-forge
  target_map=kingdom-7
  inviter=Alex
  expires_at=...
        ↓
Steve sees:
"This world requires Fantasy Runtime."
[Install / Launch Runtime]
        ↓
Modrinth Server Project
        ↓
installs/updates required content
        ↓
launches the correct Minecraft runtime into your public server
        ↓
NetworkBridge authenticates Steve
        ↓
looks up pending invite
        ↓
World Controller starts/resolves kingdom-7
        ↓
Velocity transfers Steve
```

The launcher restart is real, but the user does **not** need to manually discover mods, loader versions, or server addresses.

---

# 10. Plain-English glossary

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

## StatefulSet
A Kubernetes workload type with stable identity that fits persistent server instances and PVC-backed worlds.

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

---

# Part II — How to interpret the actual tools

# 11. Capability cheat sheet

| Component | Proxy routing | Social | Dynamic K8s lifecycle | Protocol versions | Client mod install | Persistent world storage |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| Velocity | ✅ | plugin layer | ❌ | plugin layer | ❌ | ❌ |
| Gate classic | ✅ | custom/API layer | ❌ | ✅ ViaLite path | ❌ | ❌ |
| TAB | ❌ | display only | ❌ | ❌ | ❌ | ❌ |
| ViaVersion/Backwards | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| Nakama | ❌ MC routing | ✅ | external integration | ❌ | ❌ | metadata only |
| mc-router | hostname edge routing | ❌ | ✅ limited 0↔1 StatefulSet wake | ❌ | ❌ | ❌ |
| World Controller | policy decision | integrates | ✅ | compatibility metadata | launcher link selection | coordinates PVC workload |
| itzg/minecraft-server | ❌ | ❌ | runs inside K8s | server-specific | server-side pack install | with PVC |
| Agones | connection allocation | ❌ | ✅ ephemeral/session model | ❌ | ❌ | not the default persistence model |
| Modrinth Server Projects | ❌ | ❌ | ❌ | selects correct runtime | ✅ | ❌ |
| packwiz | ❌ | ❌ | ❌ | pack definition | ✅ pre-launch/update workflow | ❌ |

The boundaries are deliberate.

---

# 12. Maturity and deployment tiers

## Tier A — foundation

Use immediately:

```text
Velocity
TAB
ViaVersion + ViaBackwards
itzg/minecraft-server
StatefulSet + PVC
World Controller
```

These form the minimum dynamic network.

---

## Tier B — product/social layer

Add next:

```text
Nakama
CockroachDB
NetworkBridge
friends
parties
invites
presence
world browser
```

---

## Tier C — operational efficiency

Add after basic switching works:

```text
mc-router
scale-to-zero
idle draining
Prometheus metrics
backups
```

---

## Tier D — client-runtime UX

Add once modded fantasy is stable:

```text
Modrinth Server Project
packwiz CI
pending cross-runtime invite
```

---

## Tier E — session matchmaking

Add only when needed:

```text
Agones
warm fleets
atomic GameServerAllocation
FleetAutoscaler
```

---

# 13. Current verification notes — 2026-08-19

## Velocity

Verified against current PaperMC docs/repository.

Important current facts:

```text
Java 25 minimum in current getting-started docs
4.0.0 release line exists in 2026
modern forwarding remains recommended for 1.13+
Paper has native modern forwarding
Forge 1.13–1.20.1 requires Ambassador for Velocity compatibility
ProxyCompatibleForge supplies modern forwarding for Forge 1.14+
```

Use the **stable release line**, not a snapshot merely because a container can download one.

---

## Gate

Verified against current Gate docs/repository.

Important current facts:

```text
Gate classic supports managed ViaLite path
modded compatibility docs cover Forge 1.13–1.20.1
Gate Lite is hostname reverse-proxy oriented
full/classic mode is the relevant comparison to Velocity
```

Selected as an alternative, not the default.

---

## TAB

Verified current release: **6.1.2** in August 2026.

It supports Velocity and can consume MiniPlaceholders.

Use the proxy-level TAB plugin for global player display.

Exact internal world/dimension still comes from your bridge/control plane.

---

## ViaVersion / ViaBackwards

Verified current release line: **5.11.0**, July 2026.

Use:

```text
ViaVersion   -> newer client to older supported server protocol
ViaBackwards -> older client to newer supported server protocol
```

Always test each runtime combination; “protocol connects” does not guarantee every gameplay mechanic is perfect.

---

## Nakama

Verified current release: **3.40.0**, July 13, 2026.

Current documentation supports the needed concepts:

```text
friends
status/presence
parties
party invites
chat/streams
matchmaking/listing primitives
custom runtime functions
```

Current server configuration documentation treats CockroachDB as the production-supported database. Some install examples still mention PostgreSQL for development, but do not make PostgreSQL the production Nakama database in this architecture.

---

## itzg/minecraft-server

Verified current release line: **2026.8.0**, August 4, 2026.

It remains an actively maintained general Minecraft Java container image that can install versions, loaders and modpacks.

---

## itzg/mc-proxy

Current documentation provides a `java25` variant.

Use it for modern Velocity because current Velocity requires Java 25.

Before production, pin the exact image version/digest rather than following a floating tag.

---

## mc-router

Current repository documentation verifies:

```text
hostname-based routing
Kubernetes discovery
Docker discovery
StatefulSet scale 0↔1
webhook integration
metrics
optional proxyServerName routing through Velocity/Bungee after waking backend
```

That makes it a useful edge component.

It does not replace the World Controller for in-session portal transfers.

---

## Agones

Current documentation still centers on:

```text
Fleet
GameServerAllocation
FleetAutoscaler
buffer/webhook autoscaling
```

This is mature and useful for disposable/warm session servers.

Use it selectively rather than wrapping every persistent survival world in it.

---

## Modrinth Server Projects

Introduced in 2026 specifically around seamless server compatibility.

Current flow can associate a server with required modded content so the Modrinth App can install the requirements and launch directly into the server.

This is the strongest existing public UX primitive for your cross-runtime invite problem.

It still does not hot-load a new Forge/NeoForge/Fabric classpath into an already-running incompatible Minecraft process.

---

# 14. Failure modes you must design for

## World is “Running” but Minecraft is not ready

Bad:

```text
Pod phase = Running
-> transfer player
```

Better:

```text
Pod Ready
AND
Minecraft status/ping successful
AND
backend registered
-> transfer
```

---

## Two players wake the same world simultaneously

Use an idempotent transition:

```text
ensureWorldReady(map_id)
```

not:

```text
startWorld(map_id)
```

The call must safely converge if ten requests arrive simultaneously.

---

## Party is split during transfer

Reserve capacity for the full party.

Do not independently random-route members.

---

## Invite target changed during launcher restart

Pending invite should contain:

```text
inviter
target runtime
target map
creation time
expiry
policy
```

On reconnect:

```text
if inviter moved and policy=follow_player:
    resolve new location
else:
    use original target map
```

Make this explicit.

---

## Modded map updates while players have old runtime

Never mutate a runtime contract without versioning it.

Bad:

```text
fantasy-runtime -> silently replace 15 required mods
```

Better:

```text
fantasy-1.20.1-r3
fantasy-1.20.1-r4
```

Drain r3 and migrate intentionally.

---

## Community map contains malicious or broken content

Treat uploaded worlds as untrusted.

Perform:

```text
size limits
archive validation
path traversal protection
malware scan
allowed file-type checks
no arbitrary startup scripts
runtime-class allowlist
server-side plugin/mod allowlist
manual approval for executable additions
```

---

## Sleeping world never wakes

Timeout and fall back:

```text
start
  ↓ timeout
mark DEGRADED
  ↓
return player to lobby
  ↓
surface operator alert
```

Never leave the player in an infinite “Connecting…” loop.

---

## Backend becomes publicly reachable

This is a serious authentication/security failure because backend servers are normally in offline mode behind the proxy.

Use:

```text
public exposure: proxy only
backend Services: ClusterIP
network policy/firewall
Velocity modern forwarding secret
```

Do not rely on forwarding secrets as the only firewall.

---

# 15. Observability

Track per world:

```text
state
players
reserved_slots
runtime_id
start latency
Minecraft-ready latency
last activity
idle duration
CPU
memory
tick time / MSPT
TPS
disk usage
save duration
```

Track routing:

```text
invite accept latency
world wake success rate
world wake p50/p95
portal transfer success
random-map selection count
failed compatibility checks
launcher-transition count
pending-invite completion rate
```

Track proxy:

```text
connected players
backend connection failures
protocol translation failures
Forge handshake failures
transfer latency
```

Track social:

```text
party creation
invite acceptance
pending invite expiry
presence update failures
```

The most useful product metric is:

```text
time from "Join friend" click
to "player can move in friend's world"
```

Measure it separately for:

```text
same runtime / awake world
same runtime / sleeping world
cross-runtime install+launch
```

---

# 16. Security boundaries

## Public network boundary

Expose only:

```text
Velocity / mc-router Minecraft entry
Nakama only if you intentionally need public client API
web UI endpoints you explicitly publish
```

Backends remain private ClusterIP services.

---

## Kubernetes RBAC boundary

World Controller:

```text
get/list/watch pods
get/list/watch services
get/list/watch/patch StatefulSets
optional create/delete only in map namespace if design requires it
```

Avoid:

```text
cluster-admin
arbitrary Secret read
arbitrary workload exec
host access
```

---

## Proxy plugin boundary

NetworkBridge should call the World Controller.

It should **not** receive a Kubernetes admin kubeconfig.

---

## Community map boundary

A map definition is data.

A new executable plugin/mod is code.

Do not make “upload map” equivalent to “execute arbitrary jar.”

---

# Part III — Step-by-step implementation

# 17. Phase 0 — Decide names before deploying

Use stable identifiers.

Example:

```text
Kubernetes namespace: minecraft
Public host: play.example.com

Runtime IDs:
  vanilla-current
  backrooms-current
  fantasy-1.20.1-forge

Backend logical IDs:
  lobby-1
  survival-main
  backrooms-001
  fantasy-kingdom-001
```

Do not use user-facing display names as primary keys.

---

# 18. Phase 1 — Create repository structure

Recommended Git repository:

```text
minecraft-platform/
├── README.md
├── clusters/
│   └── alpha/
│       ├── namespace.yaml
│       ├── velocity/
│       ├── nakama/
│       ├── cockroachdb/
│       ├── mc-router/
│       └── monitoring/
├── runtimes/
│   ├── vanilla-current/
│   │   ├── runtime.yaml
│   │   └── server/
│   ├── backrooms-current/
│   │   ├── runtime.yaml
│   │   └── server/
│   └── fantasy-1.20.1-forge/
│       ├── runtime.yaml
│       ├── packwiz/
│       └── server/
├── maps/
│   ├── survival-main/
│   │   └── map.yaml
│   └── backrooms-level-0/
│       └── map.yaml
├── services/
│   ├── world-controller/
│   └── network-bridge/
└── docs/
```

Goal:

```text
Git says what SHOULD exist.
Kubernetes says what IS running.
Nakama says what PLAYERS are doing.
```

---

# 19. Phase 2 — Create Kubernetes namespaces

Starter:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: minecraft
---
apiVersion: v1
kind: Namespace
metadata:
  name: minecraft-system
```

Suggested separation:

```text
minecraft
  -> actual game servers

minecraft-system
  -> proxy, world-controller, social bridge, mc-router
```

If you already have tenant-specific namespace policy, adapt this rather than bypassing it.

Apply:

```bash
kubectl apply -f clusters/alpha/namespace.yaml
```

---

# 20. Phase 3 — Deploy CockroachDB and Nakama

## 20.1 Why CockroachDB

For production Nakama in this design, follow current Nakama documentation and use CockroachDB.

Do not choose PostgreSQL merely because older/community examples are familiar.

---

## 20.2 Deploy CockroachDB

Prefer CockroachDB's current supported Helm deployment for Kubernetes.

Conceptually:

```text
CockroachDB StatefulSet
  + persistent volume
  + internal Service
  + backups
```

For a single-node homelab you may intentionally run a one-node database, but understand:

```text
one node != database high availability
```

The social service can be rebuilt; its durable database still needs backups.

---

## 20.3 Deploy Nakama 3.40.0

Pin:

```text
Nakama: 3.40.0
```

Do not use `latest` in production manifests.

Nakama needs:

```text
database address
server key
console credentials
runtime module volume, if custom server runtime is used
```

Expose Nakama internally first.

Example service intent:

```text
nakama.minecraft-system.svc.cluster.local
```

Do not expose its console publicly without authentication/network controls.

---

## 20.4 Create Minecraft identity authentication

When a player first connects through authenticated Velocity:

```text
Velocity UUID
   ↓
NetworkBridge
   ↓
Nakama custom authentication
   ↓
Nakama user
```

Use UUID as the stable custom ID.

Pseudo-flow:

```java
String minecraftUuid = player.getUniqueId().toString();

NakamaSession session =
    nakama.authenticateCustom(minecraftUuid, true, player.getUsername());
```

Store the Nakama session/token server-side, not on the vanilla Minecraft client.

---

## 20.5 First test

Acceptance criteria:

```text
[ ] player joins Velocity
[ ] NetworkBridge can authenticate/find Nakama account
[ ] reconnect returns same Nakama identity
[ ] username changes do not create new social identity
```

Do not proceed to parties until this is deterministic.

---

# 21. Phase 4 — Deploy Velocity

## 21.1 Use Java 25

Current PaperMC documentation requires Java 25.

If using `itzg/mc-proxy`, use its Java 25 variant.

Example conceptual Deployment:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: velocity
  namespace: minecraft-system
spec:
  replicas: 1
  selector:
    matchLabels:
      app: velocity
  template:
    metadata:
      labels:
        app: velocity
    spec:
      containers:
        - name: velocity
          image: itzg/mc-proxy:java25
          env:
            - name: TYPE
              value: VELOCITY
            - name: MEMORY
              value: 1G
          ports:
            - containerPort: 25577
              name: minecraft
```

**Production note:** pin the image digest or tested release tag after validation.

---

## 21.2 Create forwarding secret

Generate a strong random secret:

```bash
openssl rand -base64 48
```

Store it as a Kubernetes Secret.

Do not commit it to Git.

Velocity:

```toml
player-info-forwarding-mode = "modern"
forwarding-secret-file = "forwarding.secret"
```

---

## 21.3 Configure initial backend

Start with exactly one backend:

```toml
[servers]
lobby = "lobby.minecraft.svc.cluster.local:25565"

try = ["lobby"]
```

Do not begin with dynamic registration before static connectivity works.

---

## 21.4 Public exposure

Expose Velocity, not backend servers.

Desired network:

```text
Internet
   ↓
Velocity Service / relay
   ↓
ClusterIP Minecraft backend
```

Acceptance criteria:

```text
[ ] public client reaches Velocity
[ ] player authenticates in online mode at proxy
[ ] lobby cannot be reached directly from public Internet
```

---

# 22. Phase 5 — Deploy the Paper lobby

Use `itzg/minecraft-server`.

Conceptual StatefulSet:

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: lobby
  namespace: minecraft
spec:
  serviceName: lobby
  replicas: 1
  selector:
    matchLabels:
      app: lobby
  template:
    metadata:
      labels:
        app: lobby
    spec:
      containers:
        - name: minecraft
          image: itzg/minecraft-server:2026.8.0
          env:
            - name: EULA
              value: "TRUE"
            - name: TYPE
              value: "PAPER"
            - name: ONLINE_MODE
              value: "FALSE"
          ports:
            - containerPort: 25565
```

Backend offline mode is acceptable **only because the backend is private behind the authenticated proxy**.

---

## 22.1 Configure Paper modern forwarding

Current PaperMC guidance:

`server.properties`:

```properties
online-mode=false
```

`spigot.yml`:

```yaml
settings:
  bungeecord: false
```

`config/paper-global.yml`:

```yaml
proxies:
  velocity:
    enabled: true
    online-mode: true
    secret: "THE_SAME_FORWARDING_SECRET"
```

Prefer templating/mounting the secret rather than writing it into Git.

---

## 22.2 Verify identity

Inside lobby:

```text
player UUID seen by backend
==
authenticated UUID seen by Velocity
```

If not, stop and fix forwarding before adding social state.

---

# 23. Phase 6 — Install TAB

Use current stable TAB release.

At audit time:

```text
TAB 6.1.2
```

Install TAB on Velocity.

Start with server-level display:

```text
Lobby
  Steve
  Alex

Survival
  Ahmad
```

Do not attempt exact dimensions yet.

---

## 23.1 Add MiniPlaceholders if needed

TAB on Velocity can integrate with MiniPlaceholders.

Later your NetworkBridge can expose values such as:

```text
<network_runtime>
<network_map>
<network_dimension>
<network_party>
```

Acceptance criteria:

```text
[ ] every online player appears globally
[ ] server grouping is correct
[ ] switching backend updates TAB
```

---

# 24. Phase 7 — Add ViaVersion and ViaBackwards

At audit time:

```text
ViaVersion 5.11.0
ViaBackwards 5.11.0
```

Install on the proxy unless your compatibility test matrix requires a different placement.

Build an explicit compatibility matrix.

Example:

| Client | Backend runtime | Expected |
|---|---|---|
| current Java | current Paper | native |
| newer Java | older Paper | ViaVersion test |
| older supported Java | newer Paper | ViaBackwards test |
| vanilla client | Forge fantasy requiring mods | reject / launcher transition |

Do not say:

```text
ViaVersion installed -> every Minecraft version is now supported
```

Treat compatibility as tested contracts.

---

# 25. Phase 8 — Deploy the Forge 1.20.1 fantasy runtime

This runtime is special.

Velocity's current compatibility docs say Forge versions 1.13–1.20.1 are not natively supported by Velocity; use **Ambassador**.

Therefore:

```text
Velocity
  + Ambassador
        ↓
Forge 1.20.1
  + ProxyCompatibleForge
```

ProxyCompatibleForge supplies Velocity modern forwarding support for Forge.

---

## 25.1 Pin the fantasy runtime

Do not use loose ranges.

Record:

```yaml
id: fantasy-1.20.1-forge
minecraft_version: "1.20.1"
loader: forge
loader_version: "PIN_EXACT_TESTED_VERSION"
pack_revision: "r1"
```

Pack revision should change when required client dependencies change.

---

## 25.2 Author the pack

Recommended:

```text
packwiz repository
  ↓ CI export
Modrinth pack/server project
```

packwiz gives you Git-friendly source control.

Modrinth gives players the usable installer/launcher experience.

---

## 25.3 Server installation

Use `itzg/minecraft-server` with the selected modpack installation method.

Mount the world to a PVC.

Do not let the world directory disappear with the Pod.

---

## 25.4 Test proxy switching

Test:

```text
correct fantasy client
lobby -> fantasy
fantasy -> lobby
fantasy backend A -> compatible fantasy backend B
```

Then test wrong runtime:

```text
vanilla client -> fantasy
```

Expected behavior should be a controlled denial/launcher instruction, not a cryptic Forge registry error.

---

# 26. Phase 9 — Define the runtime catalog

Create `runtimes/<id>/runtime.yaml`.

Example:

```yaml
apiVersion: platform.example/v1
kind: RuntimeDefinition
metadata:
  id: backrooms-current

spec:
  minecraft:
    serverType: PAPER
    version: "PIN_TESTED_VERSION"

  client:
    modpackRequired: false
    resourcePackRequired: true

  routing:
    viaCompatible: true
    randomPoolEligible: true

  contentPolicy:
    allowWorldUpload: true
    allowPluginsFromMap: false
    allowClientModsFromMap: false

  resources:
    requests:
      cpu: "1"
      memory: "2Gi"
    limits:
      cpu: "4"
      memory: "6Gi"
```

This does not have to be a Kubernetes CRD initially.

It can be your own YAML schema consumed by the World Controller.

Start simple.

---

# 27. Phase 10 — Define map metadata

Example:

```yaml
apiVersion: platform.example/v1
kind: MapDefinition

metadata:
  id: backrooms-level-0
  displayName: "Backrooms — Level 0"
  creatorId: "user-123"

spec:
  runtimeId: backrooms-current

  persistence: persistent

  capacity:
    maxPlayers: 12

  routing:
    public: true
    randomEligible: true
    allowPartyJoin: true
    weight: 1.0

  tags:
    - horror
    - backrooms
    - community

  world:
    pvc: backrooms-level-0-world

  idle:
    sleepAfterSeconds: 600
```

Separate:

```text
MapDefinition = what the world is
MapInstance   = current running state
```

---

# 28. Phase 11 — Build the World Controller

Choose a boring implementation language you operate well.

Good options:

```text
Go
Python/FastAPI
Kotlin/Java
```

The service is not latency-critical compared with Minecraft startup time.

Correctness matters more.

---

## 28.1 Minimal API

Start with:

```http
GET /v1/maps
GET /v1/maps/{map_id}
GET /v1/instances/{map_id}

POST /v1/instances/{map_id}/ensure-ready
POST /v1/instances/{map_id}/reserve
POST /v1/routes/random
POST /v1/instances/{map_id}/release
```

Do not begin with 50 endpoints.

---

## 28.2 `ensure-ready`

Pseudo-code:

```python
async def ensure_ready(map_id):
    map_def = catalog.get(map_id)

    assert map_def.enabled

    runtime = runtimes.get(map_def.runtime_id)

    sts = k8s.get_statefulset(map_def.instance_name)

    if sts.spec.replicas == 0:
        k8s.scale_statefulset(sts, 1)

    await wait_for_pod_ready(sts)
    await wait_for_minecraft_ready(map_def.service_host, 25565)

    await proxy_registry.ensure_registered(
        server_id=map_def.id,
        address=map_def.service_host
    )

    return {
        "state": "READY",
        "server_id": map_def.id,
        "runtime_id": runtime.id
    }
```

This operation must be idempotent.

---

## 28.3 Readiness is two-stage

Kubernetes readiness:

```text
Pod Ready
```

Minecraft readiness:

```text
status/ping succeeds
```

Use both.

For Forge, startup can take substantially longer than a small Paper map.

Set per-runtime startup timeout.

---

## 28.4 RBAC

World Controller ServiceAccount should have only what it needs.

Example intent:

```yaml
rules:
  - apiGroups: ["apps"]
    resources: ["statefulsets", "statefulsets/scale"]
    verbs: ["get", "list", "watch", "patch", "update"]

  - apiGroups: [""]
    resources: ["pods", "services"]
    verbs: ["get", "list", "watch"]
```

Adjust to exact Kubernetes API behavior and your implementation.

Do not grant cluster-admin.

---

# 29. Phase 12 — Build NetworkBridge for Velocity

This is the glue plugin.

Responsibilities:

```text
authenticate Minecraft UUID with Nakama
implement /worlds
implement /join
implement /invite
implement /party
call World Controller
register dynamic backend routes
connect player after readiness
publish MiniPlaceholders
maintain presence
```

---

## 29.1 Never let the plugin directly scale Kubernetes

Bad:

```text
Velocity plugin
  -> cluster-admin kubeconfig
```

Good:

```text
Velocity plugin
  -> mTLS/internal HTTP
  -> World Controller
  -> narrow RBAC
```

---

## 29.2 Dynamic backend registration

When World Controller returns:

```json
{
  "server_id": "backrooms-level-0",
  "host": "backrooms-level-0.minecraft.svc.cluster.local",
  "port": 25565
}
```

NetworkBridge can register/update the Velocity backend and then connect the player.

Pseudo-Java:

```java
ServerInfo info = new ServerInfo(
    serverId,
    new InetSocketAddress(host, port)
);

RegisteredServer server =
    proxyServer.registerServer(info);

player.createConnectionRequest(server)
      .connect();
```

Your real implementation should handle races and already-registered servers.

---

# 30. Phase 13 — Implement friends and parties

Do this before random routing.

Commands:

```text
/friend add <player>
/friend accept <player>
/friends

/party create
/party invite <player>
/party accept <player>
/party leave
```

Back them with Nakama.

Acceptance criteria:

```text
[ ] friend survives Minecraft reconnect
[ ] party state is visible across backends
[ ] invite can be accepted from a different backend
[ ] party leader can request a world for entire party
```

---

# 31. Phase 14 — Implement `/join <friend>`

Algorithm:

```text
/join Alex
    ↓
resolve Alex Nakama user
    ↓
read presence
    ↓
is joinable?
    ↓
is runtime compatible with caller's current runtime?
```

If compatible:

```text
ensure target world ready
reserve one slot
transfer
```

If incompatible:

```text
create pending cross-runtime invite/join
show required runtime
offer launcher/server-project action
```

---

# 32. Phase 15 — Implement pending cross-runtime invites

Data contract:

```json
{
  "id": "invite-uuid",
  "recipient_minecraft_uuid": "...",
  "inviter_minecraft_uuid": "...",
  "target_runtime_id": "fantasy-1.20.1-forge",
  "target_map_id": "fantasy-kingdom-001",
  "mode": "FOLLOW_INVITER",
  "created_at": "2026-08-19T...",
  "expires_at": "2026-08-19T..."
}
```

When the player reconnects:

```text
player authenticated
    ↓
NetworkBridge queries pending joins
    ↓
validate current client/runtime compatibility
    ↓
resolve target
    ↓
ensure-ready
    ↓
transfer
    ↓
consume pending join
```

This is what makes the restart feel like one continuous invite flow.

---

# 33. Phase 16 — Publish Modrinth Server Projects

Create one server/runtime project per client-required runtime.

For example:

```text
Your Network — Fantasy Runtime
```

Compatibility:

```text
Minecraft 1.20.1
Forge
exact required modpack
```

The user-facing goal:

```text
"Join Fantasy"
    ↓
Modrinth shows required content
    ↓
install/update
    ↓
launch into your server
```

Do not create a separate project for every map when all maps use the same fantasy runtime.

Create a project per **runtime compatibility contract**.

---

# 34. Phase 17 — Add packwiz CI

Use packwiz as the source-of-truth for the mod list if you want Git review.

Example flow:

```text
pull request modifies pack.toml / index
    ↓
CI validates
    ↓
export Modrinth pack
    ↓
test server starts
    ↓
integration test connects
    ↓
publish runtime revision
```

Keep:

```text
r1
r2
r3
```

for breaking pack changes.

---

# 35. Phase 18 — Add exact world/dimension TAB information

Backend bridge sends world change:

```json
{
  "player_uuid": "...",
  "runtime_id": "vanilla-current",
  "map_id": "survival-main",
  "dimension": "minecraft:the_nether"
}
```

Store/update presence.

NetworkBridge exposes:

```text
<network_map>
<network_runtime>
<network_dimension>
```

TAB then displays:

```text
Fantasy Kingdom
  Ahmad — Overworld
  Alex  — The Nether

Backrooms
  Steve — Level 0
```

Do not infer dimension from proxy server name.

---

# 36. Phase 19 — Implement the glitch/random portal

Backend trigger:

```text
player touches portal region
```

Request:

```http
POST /v1/routes/random
```

Body:

```json
{
  "player_uuid": "...",
  "party_id": null,
  "runtime_id": "backrooms-current",
  "tags": ["backrooms"],
  "exclude_recent": true
}
```

Selection pipeline:

```text
all maps
    ↓
enabled?
    ↓
runtime compatible?
    ↓
random eligible?
    ↓
capacity?
    ↓
party policy?
    ↓
not recently visited?
    ↓
weighted random
```

Then:

```text
reserve
ensure-ready
play glitch audiovisual effect
transfer
```

---

## 36.1 Never randomly select an incompatible client runtime

Bad:

```text
vanilla player
-> random
-> Forge-only map
-> disconnect with missing mods
```

Good:

```text
random pool is filtered by current runtime
```

If you want a cross-runtime “mystery invite,” make it an explicit launcher transition experience.

---

# 37. Phase 20 — Add mc-router

Use `mc-router` for cases where players enter through different hostnames or sleeping services should wake at the edge.

Example:

```text
survival.example.com
map-123.example.com
```

`mc-router` can discover annotated Kubernetes services and can scale a StatefulSet from 0 to 1.

It can also use a proxy server name so the final player route still goes to Velocity after the backend is awakened.

---

## 37.1 Why World Controller still remains

New external connection:

```text
client -> mc-router -> wake -> Velocity
```

Existing connected player:

```text
player in Velocity -> portal
```

The second path bypasses the public edge handshake.

Therefore:

```text
mc-router = edge wake/routing
World Controller = authoritative in-game lifecycle
```

---

## 37.2 Prefer webhook isolation if desired

`mc-router` supports webhook integration.

A hardened design can keep Kubernetes mutation permission in the World Controller rather than giving `mc-router` broad credentials.

Pattern:

```text
mc-router
   ↓ webhook
World Controller
   ↓ K8s
```

---

# 38. Phase 21 — Add idle sleep

For persistent worlds:

```text
last player leaves
    ↓
start idle timer
    ↓
new reservation?
  yes -> cancel sleep
  no  -> continue
    ↓
request graceful save/stop
    ↓
wait process exit
    ↓
scale StatefulSet to 0
```

Do not `SIGKILL` an actively saving world as your normal sleep method.

---

## 38.1 Separate “empty” from “safe to stop”

A server may be empty but still:

```text
saving
running maintenance
executing a migration
reserved for a joining party
```

Track:

```text
player_count
reservation_count
draining
maintenance_lock
```

Sleep only when all permit it.

---

# 39. Phase 22 — Add Agones only for session worlds

Install Agones when you have a workload such as:

```text
Backrooms run
Dungeon run
Minigame
Disposable generated challenge
```

Use:

```text
Fleet
    ↓
Ready GameServers
    ↓
GameServerAllocation
    ↓
Allocated session
    ↓
session ends
    ↓
shutdown/replacement
```

A Fleet Autoscaler can keep a buffer of ready capacity.

Do not replace your persistent PVC-backed survival worlds with this unless you intentionally redesign their persistence model.

---

# 40. Phase 23 — Add AI proximity chat

Keep AI bots as special actors, not every MineColonies citizen.

Input gate:

```text
chat event
    ↓
same backend?
    ↓
same dimension?
    ↓
sender entity loaded?
    ↓
distance <= hearing radius?
    ↓
LLM
```

Example:

```python
if sender.backend_id != bot.backend_id:
    return

if sender.dimension != bot.dimension:
    return

if distance(sender.position, bot.position) > 12:
    return

respond_with_llm()
```

Presence/network state can tell you **where** the bot/player is.

Actual entity distance should be computed by the backend bot/mod where positions are authoritative.

---

# 41. Phase 24 — Community map upload pipeline

Do not mount arbitrary user archives directly into a running server.

Pipeline:

```text
upload
  ↓
quarantine object storage
  ↓
size/type validation
  ↓
safe archive extraction
  ↓
malware scan
  ↓
world structure validation
  ↓
runtime compatibility validation
  ↓
review / automated policy
  ↓
publish immutable map revision
  ↓
create/update MapDefinition
```

A map revision should be immutable once published.

Example:

```text
backrooms-level-0@v1
backrooms-level-0@v2
```

---

# 42. Phase 25 — Backups

Persistent worlds:

```text
PVC
  ↓
Minecraft save / quiesce
  ↓
snapshot/backup
  ↓
off-machine copy
```

Do not call a backup successful merely because a file exists.

Test restores.

Minimum test:

```text
[ ] delete disposable test instance
[ ] restore world to new PVC
[ ] boot server
[ ] verify known structures/player data
```

Also back up:

```text
CockroachDB
runtime/map Git repo
Nakama runtime config
Velocity config
secrets through your secret-management process
```

---

# 43. Phase 26 — Monitoring

Use your existing Prometheus/Grafana stack.

World Controller metrics:

```text
minecraft_world_start_seconds
minecraft_world_start_failures_total
minecraft_world_ready
minecraft_world_players
minecraft_world_reservations
minecraft_route_requests_total
minecraft_route_failures_total
```

Proxy:

```text
connected players
backend connection failures
transfer latency
```

Minecraft server:

```text
TPS
MSPT
heap
CPU
memory
disk
```

Alert on:

```text
world startup failures
repeated crash loop
disk pressure
PVC nearly full
CockroachDB unavailable
Nakama unavailable
Velocity backend failure spike
```

---

# 44. Phase 27 — Rollout order

Use this exact order:

```text
1. Velocity + one static Paper lobby
2. secure forwarding + backend isolation
3. TAB
4. ViaVersion/Backwards compatibility test
5. Nakama identity mapping
6. friends + parties
7. one static second backend + /join
8. World Controller
9. one persistent StatefulSet scale-to-zero map
10. portal -> wake -> transfer
11. exact map presence + TAB
12. random compatible map
13. fantasy Forge runtime + Ambassador + ProxyCompatibleForge
14. Modrinth Server Project
15. pending cross-runtime invite
16. mc-router edge wake
17. community upload pipeline
18. optional Agones ephemeral fleet
19. AI proximity bot
```

This order intentionally proves one contract at a time.

---

# Part IV — Technical reference

# 45. Recommended source-of-truth model

```text
Git:
  runtime definitions
  map definitions
  Kubernetes manifests
  packwiz manifests
  policy

Kubernetes:
  actual server process state
  pods
  services
  PVCs
  StatefulSet replicas

Nakama:
  user/social state
  friends
  parties
  invites
  presence
  pending joins

World Controller:
  derived live routing state
  readiness
  reservations
  lifecycle locks
```

Do not duplicate every fact into every database.

---

# 46. RuntimeDefinition schema

Illustrative:

```yaml
metadata:
  id: fantasy-1.20.1-forge
  revision: r1

minecraft:
  version: "1.20.1"
  serverType: FORGE
  loaderVersion: "PIN_ME"

client:
  required: true
  distribution: modrinth-server-project
  projectId: "PIN_ME"

proxy:
  kind: velocity
  ambassadorRequired: true
  modernForwarding: true

routing:
  instantSwitchWithinRuntime: true
  viaTranslationAllowed: false

resources:
  memory: 12Gi
  cpuLimit: "8"

startup:
  timeoutSeconds: 300

idle:
  sleepAllowed: true
  timeoutSeconds: 1200
```

---

# 47. MapInstance schema

```json
{
  "map_id": "fantasy-kingdom-001",
  "runtime_id": "fantasy-1.20.1-forge",
  "state": "READY",
  "backend_id": "fantasy-kingdom-001",
  "service_host": "fantasy-kingdom-001.minecraft.svc.cluster.local",
  "port": 25565,
  "players": 4,
  "reservations": 1,
  "max_players": 12,
  "last_activity": "2026-08-19T...",
  "revision": 14
}
```

Use a revision/version for optimistic concurrency if state is persisted outside Kubernetes.

---

# 48. Routing state machine

```text
REQUESTED
    │
    ├── incompatible runtime ─────► CLIENT_TRANSITION_REQUIRED
    │
    └── compatible
            │
            ▼
         RESERVING
            │
            ▼
         STARTING
            │
            ▼
     WAITING_K8S_READY
            │
            ▼
      WAITING_MC_READY
            │
            ▼
        REGISTERING
            │
            ▼
         TRANSFERRING
            │
            ├── success ─────────► COMPLETE
            │
            └── failure ─────────► RELEASE_RESERVATION -> FAILED
```

Every stage should have timeout/error handling.

---

# 49. Random routing scoring

Do not use pure random if maps differ in health and capacity.

Example:

```python
eligible = [
    m for m in maps
    if m.enabled
    and m.runtime_id == player.runtime_id
    and m.random_eligible
    and m.free_slots >= party_size
]

for m in eligible:
    score = (
        m.weight
        * freshness_factor(m)
        * health_factor(m)
        * capacity_factor(m)
        * novelty_factor(player, m)
    )

selected = weighted_random(eligible, score)
```

This lets you prefer:

```text
healthy
underused
new
not recently visited
community-promoted
```

without violating compatibility.

---

# 50. Invite policy

Possible invite modes:

```text
JOIN_MAP
FOLLOW_PLAYER
JOIN_PARTY
JOIN_SESSION
```

Recommended default for friend invites:

```text
FOLLOW_PLAYER until accepted
then freeze target during transfer
```

This prevents chasing a friend across servers while startup is in progress.

---

# 51. World readiness contract

World Controller returns READY only when:

```text
StatefulSet desired replicas >= 1
Pod Ready
Service endpoints exist
Minecraft status check succeeds
runtime revision matches expected revision
server is not draining
capacity reservation is available
```

This contract is more useful than a generic `/healthz`.

---

# 52. Network security checklist

```text
[ ] only proxy/edge is publicly exposed
[ ] backend Minecraft Services are ClusterIP
[ ] backend online-mode=false only behind proxy
[ ] Velocity modern forwarding enabled
[ ] forwarding secret stored outside Git
[ ] Forge backend uses ProxyCompatibleForge
[ ] Forge 1.20.1 route uses Ambassador
[ ] NetworkBridge does not have K8s cluster-admin
[ ] World Controller uses narrow ServiceAccount
[ ] Nakama console is private/protected
[ ] database is not public
[ ] community uploads are quarantined
[ ] arbitrary map JAR execution is denied
[ ] image versions/digests are pinned for production
```

---

# 53. Functional acceptance test

A release is not done until this passes:

## Network

```text
[ ] vanilla player joins public address
[ ] authenticated UUID preserved on Paper
[ ] backend cannot be joined publicly
```

## Social

```text
[ ] friend add/accept works
[ ] presence shows backend/map
[ ] party persists across backend transfer
```

## Dynamic world

```text
[ ] sleeping world replicas=0
[ ] /join wakes world
[ ] player stays in lobby while starting
[ ] player transfers only after Minecraft readiness
[ ] world sleeps after configured idle time
[ ] PVC survives stop/start
```

## Random portal

```text
[ ] only runtime-compatible maps are candidates
[ ] capacity is reserved
[ ] party moves together
[ ] failed startup returns users to safe lobby
```

## Modded runtime

```text
[ ] correct fantasy pack connects
[ ] compatible fantasy backend switching works
[ ] wrong vanilla client receives controlled runtime requirement
[ ] Modrinth install/update path works
[ ] reconnect consumes pending invite
```

## TAB

```text
[ ] global users visible
[ ] server/map information updates
[ ] exact dimension updates after world change
```

---

# 54. Performance principles

The proxy is not normally the expensive part.

The heavy components are:

```text
world generation
Forge modded simulation
MineColonies pathfinding
large mob/entity counts
chunk loading
disk saves
community maps with command/entity spam
```

Therefore prioritize:

```text
pre-generation where appropriate
entity limits
runtime-specific resource limits
spark profiling
PVC/NVMe placement for active worlds
sleep unused worlds
avoid too many always-loaded dimensions
```

Do not over-engineer proxy sharding before measuring it.

---

# 55. Upgrade policy

Pin tested versions.

Example release record:

```yaml
platformRelease: 2026-08-r1

components:
  velocity: "4.0.0"
  java: "25"
  tab: "6.1.2"
  viaversion: "5.11.0"
  viabackwards: "5.11.0"
  nakama: "3.40.0"
  minecraftServerImage: "2026.8.0"
```

For components without a desired fixed semantic release in this document:

```text
pin tested container digest
record Git commit/release
upgrade in staging
```

Never let `latest` redefine production overnight.

---

# 56. Why this architecture is intentionally not “fully automatic” on day one

The difficult part is not launching another Minecraft process.

The difficult part is maintaining these invariants:

```text
correct client runtime
correct authenticated UUID
correct world revision
correct capacity
correct party routing
correct persistent data
correct readiness
correct forwarding/security
```

A small explicit World Controller is easier to reason about than chaining five “automatic server cloud” plugins whose responsibilities overlap.

Automation should come after the contracts are clear.

---

# Part V — Current verification references

The following primary/current sources were checked for this edition. Re-audit them before major upgrades because Minecraft and its ecosystem change quickly.

1. **PaperMC — Velocity Getting Started**  
   https://docs.papermc.io/velocity/getting-started/  
   Current documentation states Java 25 is required.

2. **PaperMC — Velocity repository**  
   https://github.com/PaperMC/Velocity  
   Active proxy project and 4.x development/release history.

3. **PaperMC — Velocity Server Compatibility**  
   https://docs.papermc.io/velocity/server-compatibility/  
   Documents Paper/Fabric/Forge compatibility and Ambassador for Forge 1.13–1.20.1.

4. **PaperMC — Velocity Player Information Forwarding**  
   https://docs.papermc.io/velocity/player-information-forwarding/  
   Documents modern forwarding, Paper config, FabricProxy-Lite and ProxyCompatibleForge.

5. **PaperMC — Velocity Security**  
   https://docs.papermc.io/velocity/security/  
   Explains why forwarding is not a replacement for a firewall.

6. **Minekube Gate — repository**  
   https://github.com/minekube/gate

7. **Minekube Gate — Multi-Version Support**  
   https://gate.minekube.com/guide/multi-version

8. **Minekube Gate — Modded Servers**  
   https://gate.minekube.com/guide/modded-servers

9. **Minekube Gate — Compatibility**  
   https://gate.minekube.com/guide/compatibility

10. **TAB repository/releases**  
    https://github.com/NEZNAMY/TAB  
    https://github.com/NEZNAMY/TAB/releases

11. **TAB placeholders / Velocity MiniPlaceholders integration**  
    https://github.com/NEZNAMY/TAB/wiki/Placeholders

12. **ViaVersion releases**  
    https://github.com/ViaVersion/ViaVersion/releases

13. **ViaBackwards releases**  
    https://github.com/ViaVersion/ViaBackwards/releases

14. **Heroic Labs Nakama Release Notes**  
    https://heroiclabs.com/docs/nakama/getting-started/release-notes/  
    v3.40.0 released July 13, 2026.

15. **Heroic Labs Nakama Architecture**  
    https://heroiclabs.com/docs/nakama/getting-started/architecture/  
    Presence/status, streams and realtime architecture.

16. **Heroic Labs Nakama Server Configuration**  
    https://heroiclabs.com/docs/nakama/getting-started/configuration/  
    Current production database configuration guidance.

17. **itzg/docker-minecraft-server**  
    https://github.com/itzg/docker-minecraft-server

18. **itzg/docker-minecraft-server releases**  
    https://github.com/itzg/docker-minecraft-server/releases  
    2026.8.0 released August 4, 2026.

19. **itzg/docker-mc-proxy**  
    https://github.com/itzg/docker-mc-proxy  
    Documents Java 25 image variant.

20. **itzg/mc-router**  
    https://github.com/itzg/mc-router  
    Kubernetes/Docker discovery, hostname routing, StatefulSet auto-scale and webhook behavior.

21. **Agones Fleet**  
    https://agones.dev/site/docs/reference/fleet/

22. **Agones GameServerAllocation**  
    https://agones.dev/site/docs/reference/gameserverallocation/

23. **Agones Fleet Autoscaling**  
    https://agones.dev/site/docs/advanced/scheduling-and-autoscaling/

24. **Modrinth — Introducing Server Projects**  
    https://modrinth.com/news/article/introducing-server-projects  
    2026 required-modpack server onboarding and direct launch flow.

25. **packwiz repository**  
    https://github.com/packwiz/packwiz

26. **CloudNet releases**  
    https://github.com/CloudNetService/CloudNet/releases  
    Useful alternative; 4.0 remained in RC status during this audit.

27. **Shulker repository**  
    https://github.com/jeremylvln/Shulker  
    Architecturally relevant Kubernetes Minecraft operator; re-check maintenance before adoption.

---

# 57. Final architecture recommendation

If you want one compact answer to implement:

```text
PUBLIC ENTRY
  mc-router (optional) -> Velocity 4.0.0 / Java 25

VELOCITY
  TAB 6.1.2
  ViaVersion 5.11.0
  ViaBackwards 5.11.0
  Ambassador for Forge 1.20.1
  custom NetworkBridge

SOCIAL
  Nakama 3.40.0
  CockroachDB

DYNAMIC WORLD CONTROL
  custom World Controller
  Kubernetes StatefulSet + PVC
  itzg/minecraft-server
  mc-router edge wake
  Agones only for ephemeral sessions

CLIENT RUNTIMES
  runtime classes
  Modrinth Server Projects
  packwiz as optional Git/CI source
```

And enforce this product rule:

> **A community map may be dynamic; the required client runtime must be standardized.**

That rule is what allows portals, invites, TAB information, sleeping worlds, random Backrooms routing, and modded fantasy gameplay to coexist without turning every friend invite into dependency troubleshooting.
