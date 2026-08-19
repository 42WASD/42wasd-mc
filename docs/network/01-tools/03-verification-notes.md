# Current verification notes — 2026-08-19

The audit facts for each tool. Re-audit before major upgrades.

## Velocity

- Java 25 minimum in current getting-started docs.
- 4.0.0 release line exists in 2026.
- Modern forwarding remains recommended for 1.13+.
- Paper has native modern forwarding.
- Forge 1.13–1.20.1 requires **Ambassador** for Velocity compatibility.
- **ProxyCompatibleForge** supplies modern forwarding for Forge 1.14+.

Use the **stable release line**, not a snapshot merely because a container can download one.

## Gate

- Gate classic supports a managed ViaLite path.
- Modded compatibility docs cover Forge 1.13–1.20.1.
- Gate Lite is hostname reverse-proxy oriented.
- Full/classic mode is the relevant comparison to Velocity.

Selected as an alternative, not the default.

## TAB

- Current release **6.1.2** (August 2026).
- Supports Velocity and can consume MiniPlaceholders.
- Use the proxy-level TAB plugin for global player display.
- Exact internal world/dimension still comes from your bridge/control plane.

## ViaVersion / ViaBackwards

- Current release line: **5.11.0** (July 2026).
- ViaVersion: newer client → older supported server protocol.
- ViaBackwards: older client → newer supported server protocol.
- Always test each runtime combination; "protocol connects" does not guarantee every gameplay mechanic is perfect.

## Nakama

- Current release: **3.40.0** (July 13, 2026).
- Supports: friends, status/presence, parties, party invites, chat/streams, matchmaking/listing primitives, custom runtime functions.
- CockroachDB is the production-supported database.
- Do **not** make PostgreSQL the production Nakama database.

## itzg/minecraft-server

- Current release line: **2026.8.0** (August 4, 2026).
- Actively maintained; installs versions, loaders, and modpacks.

## itzg/mc-proxy

- Provides a `java25` variant for modern Velocity.
- Pin the exact image version/digest before production rather than following a floating tag.

## mc-router

Verified: hostname-based routing, Kubernetes discovery, Docker discovery, StatefulSet scale 0↔1, webhook integration, metrics, optional `proxyServerName` routing through Velocity/Bungee after waking the backend.

Useful edge component. It does **not** replace the World Controller for in-session portal transfers.

## Agones

Current documentation still centers on `Fleet`, `GameServerAllocation`, `FleetAutoscaler`, buffer/webhook autoscaling.

Mature and useful for disposable/warm session servers. Use selectively, not for every persistent survival world.

## Modrinth Server Platform

Introduced in 2026 for seamless server compatibility. Can associate a server with required modded content so the Modrinth App installs the requirements and launches directly into the server.

The strongest existing public UX primitive for the cross-runtime invite problem. It still does **not** hot-load a new Forge/NeoForge/Fabric classpath into an already-running incompatible Minecraft process.