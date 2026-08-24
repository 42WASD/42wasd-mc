# 42wasd-mc — Minecraft Network Platform

A Kubernetes-first Minecraft network with dynamic worlds, community maps,
parties/invites, world-aware TAB, random "glitch" routing, modded fantasy
runtimes, scale-to-zero, and smooth client onboarding.

## How to use this site

- **[Setup](setup/getting-started.md)** — get oriented and up to speed.
- **[Guides](guides/architecture/index.md)** — architecture, server ops, and player experience.
- **[Reference Design](reference-design/index.md)** — the full technical design, in five parts:
  - **[I. Understand the architecture](reference-design/01-understand-the-architecture-before-installing-anything/index.md)**
  - **[II. How to interpret the tools](reference-design/02-how-to-interpret-the-actual-tools/index.md)**
  - **[III. Step-by-step implementation](reference-design/03-step-by-step-implementation/index.md)**
  - **[IV. Technical reference](reference-design/04-technical-reference/index.md)**
  - **[V. Current verification references](reference-design/05-current-verification-references/index.md)**
- **[Implementation](implementation/index.md)** — a live progress tracker for the phased build.

## The core rule

> **A community map may be dynamic; the required client runtime must be standardized.**

That rule is what lets portals, dynamic worlds, invites, TAB info, sleeping
worlds, random routing, and modded fantasy runtimes coexist without turning
every invite into dependency troubleshooting.

## Infrastructure

The hosting platform — the RKE2 cluster, hosts (`alpha`), GitOps (Argo CD), and
host-level IaC — is owned by
[42WASD/ubuntu-server-iac](https://github.com/42WASD/ubuntu-server-iac). This
repo's `infra/` carries only the Minecraft **game-layer** workloads (proxy,
lobby, Nakama, CockroachDB) that run on that platform. See
[Reference Design](reference-design/index.md) for the phased plan that builds
toward this.

Start with the [Reference Design overview](reference-design/index.md).