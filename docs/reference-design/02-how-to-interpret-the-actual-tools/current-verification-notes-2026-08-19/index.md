# Current verification notes — 2026-08-19

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

Nakama natively supports **social-provider authentication** for OAuth-first
identity: `authenticateGoogle` and `authenticateCustom` (a custom OAuth provider for Discord)
(plus the matching `link*` calls to attach additional identifiers). This makes
Nakama the canonical identity anchor for Discord/Google login; the Minecraft
UUID/name is a linked runtime binding. Discord is added as a custom OAuth
provider (not built-in), verified server-side.

Current server configuration documentation treats CockroachDB as the production-supported database. Some install examples still mention PostgreSQL for development, but do not make PostgreSQL the production Nakama database in this architecture.

---

## itzg/minecraft-server

Verified current release line: **2026.8.1**, August 19, 2026.

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
GameServerSet scale 0↔1
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

## AstralRinth (player launcher)

Verified: actively maintained fork of the Modrinth App, updated through 2026.

Why the official Modrinth App is not sufficient here:

```text
Modrinth App "offline mode" = play already-installed mods without internet
it does NOT provide offline/cracked ACCOUNT authentication
```

This architecture runs backends in offline mode behind the authenticated proxy (see Phase 6), and therefore needs a client that supports offline/cracked accounts. The official Modrinth App cannot do that.

**AstralRinth** (github.com/SmilerRyan/AstralRinth) is the candidate:

```text
fork of the Modrinth App (Theseus core)
OFFLINE AUTH for cracked + licensed accounts (also elyby)
no ads, forced telemetry/metrics disabled
macOS .dmg build (Apple Silicon / Intel) available
active fork (AstralRinth's own README + releases confirm)
```

> Note: **Migurinth** is a *different* Modrinth-App fork (in maintenance mode).
> The design pins AstralRinth specifically, not Migurinth.

It keeps the exact Modrinth App UX (modpack/mod auto-download, server-project onboarding), so players who cannot enter a world with their current client get the same "install requirements and launch directly" flow.

Caveat to record in the design:

```
It is a third-party, community-maintained fork. Pin a known-good stable build
(no dev/nightly/dirty prefix) and get it from a trusted source.
```

---
