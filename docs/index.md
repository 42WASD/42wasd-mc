# 42wasd-mc — Minecraft Network Platform

A Kubernetes-first Minecraft network with dynamic worlds, community maps, parties/invites, world-aware TAB, random "glitch" routing, modded fantasy runtimes, scale-to-zero, and smooth client onboarding.

This site is organized as a **linear, step-by-step implementation guide**. Read the understanding section first, then follow the 19 steps in order.

## How to use this guide

1. **[Understand the architecture](00-understand/index.md)** — read the mental model before touching anything.
2. **[Follow the 19 implementation steps](01-implement/index.md)** — each step is a self-contained increment with a clear goal, tasks, and an acceptance check.
3. **[Reference](02-reference/index.md)** — schemas, state machines, and technical details to look up while building.
4. **[Operations](03-operations/index.md)** — backups, monitoring, security, upgrades, performance.
5. **[Resources](04-resources/index.md)** — the verified source links (audited 2026-08-19).

## The core rule

> **A community map may be dynamic; the required client runtime must be standardized.**

That rule is what lets portals, invites, TAB info, sleeping worlds, random routing, and modded fantasy coexist without turning every invite into dependency troubleshooting.

## The 19 steps at a glance

```text
 1. Velocity + one static Paper lobby
 2. Secure forwarding + backend isolation
 3. TAB
 4. ViaVersion / ViaBackwards compatibility
 5. Nakama identity mapping
 6. Friends + parties
 7. Second static backend + /join
 8. World Controller
 9. Persistent StatefulSet scale-to-zero map
10. Portal → wake → transfer
11. Exact map presence + TAB
12. Random compatible map
13. Fantasy Forge runtime + Ambassador + ProxyCompatibleForge
14. Modrinth Server Project
15. Cross-runtime invite
16. mc-router edge wake
17. Community map upload pipeline
18. Agones ephemeral fleet (optional)
19. AI proximity bot
```

Start with the [one-sentence idea](00-understand/01-the-one-sentence-idea.md).