# 42wasd-mc — Minecraft Network Platform

A Kubernetes-first Minecraft network with dynamic worlds, community maps,
parties/invites, world-aware TAB, random "glitch" routing, modded fantasy
runtimes, scale-to-zero, and smooth client onboarding.

## How to use this site

This documentation mirrors a production-grade reference structure. Explore by
top tab:

1. **[Setup](setup/getting-started.md)** — get oriented and up to speed.
2. **[Guides](guides/architecture/index.md)** — architecture, server ops, and player experience.
3. **[Reference Design](reference-design/index.md)** — the full technical design, split into:
   - **Concepts & Design** (background),
   - **Build (Implementation Phases)**, and
   - **Reference Material**.
4. **[Implementation](implementation/index.md)** — a live progress tracker for the phased build.

## The core rule

> **A community map may be dynamic; the required client runtime must be standardized.**

That rule is what lets portals, dynamic worlds, invites, TAB info, sleeping
worlds, random routing, and modded fantasy runtimes coexist without turning
every invite into dependency troubleshooting.

## Infrastructure

The platform is operated as code from `infra/` — the single source of truth for
the hosts (Ansible), the cluster (RKE2 + Kubernetes manifests), and GitOps
(Argo CD). See [Reference Design](reference-design/index.md) for the phased plan
that builds toward this.
18. Agones ephemeral fleet (optional)
19. AI proximity bot
```

Start with the [Reference Design overview](reference-design/index.md).