# Dynamic Minecraft Network / Runtime Architecture

This section breaks the verified architecture document into **phased**, implementable pages.

> **Audit date:** 2026-08-19
> **Purpose:** define a mature, usable, Kubernetes-first architecture for a Minecraft network with dynamic worlds, community maps, parties/invites, world-aware TAB, random "glitch" routing, modded fantasy runtimes, scale-to-zero, and smooth client onboarding.

## How this section is organized

| Folder | Content |
|---|---|
| [`00-understand`](00-understand/index.md) | Part I — Understand the architecture before installing anything |
| [`01-tools`](01-tools/index.md) | Part II — How to interpret the actual tools |
| [`02-implementation`](02-implementation/index.md) | Part III — Step-by-step implementation (28 phases) |
| [`03-reference`](03-reference/index.md) | Part IV — Technical reference |
| [`04-references`](04-references/index.md) | Part V — Current verification references |

## Core product rule

> **A community map may be dynamic; the required client runtime must be standardized.**

That rule is what allows portals, invites, TAB information, sleeping worlds, random Backrooms routing, and modded fantasy gameplay to coexist without turning every friend invite into dependency troubleshooting.

## Quick start — the 19-step rollout order

The implementation is intentionally phased. Follow `02-implementation` phase-by-phase, proving one contract at a time:

```text
1.  Velocity + one static Paper lobby
2.  secure forwarding + backend isolation
3.  TAB
4.  ViaVersion/Backwards compatibility test
5.  Nakama identity mapping
6.  friends + parties
7.  one static second backend + /join
8.  World Controller
9.  one persistent StatefulSet scale-to-zero map
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

> **Note:** the source document numbers these as "Phase 0–27" for the repository/setup stages, and a separate "rollout order 1–19." This section preserves the source's numbering while grouping into deployable increments.