# Current verification notes — 2026-08-19

## Velocity

Verified against current PaperMC docs/repository.

Important current facts:

```text
Java 25 minimum in current Velocity docs
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
identity. Google is a built-in provider (`authenticateGoogle`). **Discord has
no native `authenticateDiscord` endpoint** — the documented third-party
pattern is to validate the external identity in a Nakama runtime hook
(`beforeAuthenticateCustom`) and map the verified external user ID into Nakama
**Custom Authentication**:

```text
Discord OAuth
    ↓
our auth service / Nakama beforeAuthenticateCustom hook validates the token
    ↓
obtain stable Discord user ID
    ↓
Nakama AuthenticateCustom
    ↓
Nakama account
```

So the correct description is: *"Discord OAuth is validated by our
authentication layer / Nakama runtime hook, then its verified Discord user ID
is mapped into Nakama Custom Authentication"* — not "a custom OAuth provider
for Discord" (there is no Discord provider to plug in). The Minecraft UUID/name
is a linked runtime binding, verified server-side.

Nakama requires a Postgres-wire-compatible database. Current formal Nakama docs
describe **CockroachDB as the officially supported and optimized production
target**; PostgreSQL compatibility exists and is useful for development, but it
is not the documented production recommendation. **We standardize production
on CockroachDB** (this architecture's only production DB choice).

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
native auto-scale 0↔1 (StatefulSet-only)
webhook integration
metrics
optional proxyServerName routing through Velocity/Bungee after waking backend
```

That makes it a useful edge component.

It does not replace the World Controller for in-session portal transfers.

---

## itzg/mc-monitor

Current repository documentation verifies:

```text
Minecraft protocol status/ping probe ("status" subcommand)
ping/response latency
online count / max players observation
Prometheus + Influx metrics exporter
```

**Scope: readiness & reachability, not performance.** mc-monitor reports
whether a Minecraft server answers a status/ping and how fast, plus online
count. It does **not** measure TPS, MSPT, or tick health. Those come from
backend/NetworkBridge telemetry (a plugin exporting tick health) plus spark for
profiling/diagnostics. Keep the two sources separate: mc-monitor for
readiness/reachability, backend telemetry + spark for performance.

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

This architecture runs backends in offline mode behind the authenticated proxy (see Phase 6), and therefore needs a client that can launch an offline-mode runtime.

**AstralRinth** (github.com/42WASD/AstralRinth) is the candidate:

```text
Modrinth-based launcher fork (Theseus core)
supports Microsoft, Ely.by, external OAuth Device Authorization, and offline
accounts for local/testing play
no ads, forced telemetry/metrics disabled
macOS .dmg build (Apple Silicon / Intel) available
actively maintained (AstralRinth's own README + releases confirm)
```

AstralRinth's own README describes it as a Modrinth-based launcher with
Microsoft, Ely.by, and external OAuth Device Authorization support, plus
offline accounts for local/testing use, and explicitly encourages players to
own a legitimate Minecraft license. Use that neutral framing — do not describe
it as a "pirate/cracked launcher."

> Note: **Migurinth** is a *different* Modrinth-App fork (in maintenance mode).
> The design pins AstralRinth specifically, not Migurinth.

Because AstralRinth is Modrinth-based, Modrinth **Server Project** compatibility
is a *desired capability* — but exact parity must be covered by a launcher
**acceptance test**:

```text
VERIFICATION STATUS: TEST_REQUIRED
```

Modrinth itself supports the intended flow (a Server Project defines required
pack compatibility; the Modrinth App installs the content and can launch
directly into the server), and we verified that. We did **not** verify that
AstralRinth implements every Server Project workflow identically.

> **License / ToS note.** AstralRinth's offline-account support means it can
> launch an offline-mode runtime without a Mojang/Microsoft license. That is a
> Minecraft-Terms-of-Service consideration to record as a deliberate decision.
> This design's identity model is **Nakama OAuth-first** (Discord/Google at the
> in-game auth gate, see `social-state` 7.1.0): every player — cracked *or*
> licensed — still authenticates to a verified Nakama account before leaving
> the gate. AstralRinth is therefore only the *client that can launch an
> offline-mode runtime*; it is **not** the identity authority and does not grant
> access by itself. Keep this division explicit so the offline-launcher choice
> and the OAuth-first identity anchor do not appear to conflict.

Caveat to record in the design:

```
It is a third-party, community-maintained fork. Pin a known-good stable build
(no dev/nightly/dirty prefix) and get it from a trusted source. We track the
fork under our own org (42WASD/AstralRinth) so the pinned build is ours to
re-verify, rather than a floating upstream.
```

---
