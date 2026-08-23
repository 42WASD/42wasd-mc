# Verified Dynamic Minecraft Network / Runtime Architecture

**Audit date:** 2026-08-19  
**Purpose:** define a mature, usable, Kubernetes-first architecture for a Minecraft network with dynamic worlds, community maps, parties/invites, world-aware TAB information, random “glitch” routing, modded fantasy runtimes, scale-to-zero, and the smoothest practical client onboarding.

> **Important scope note:** This is a systems-architecture and implementation guide. It deliberately separates **network routing**, **game/world lifecycle**, **social state**, **Minecraft protocol compatibility**, and **client mod/runtime distribution**. No single proxy solves all five problems, and treating them as one problem creates a fragile design.

---

---

## Platform Map

- [I — Understand the architecture before installing anything](01-understand-the-architecture-before-installing-anything/index.md)
- [II — How to interpret the actual tools](02-how-to-interpret-the-actual-tools/index.md)
- [III — Step-by-step implementation](03-step-by-step-implementation/index.md)
- [IV — Technical reference](04-technical-reference/index.md)
- [V — Current verification references](05-current-verification-references/index.md)
