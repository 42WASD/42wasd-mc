# Getting Started

This guide takes you from the high-level architecture to a running Minecraft
network. If you have not read the concepts yet, start with the
[Reference Design](../reference-design/index.md), which explains *why* the
network is built the way it is.

## What you'll build

A Kubernetes-first Minecraft network with:

- A **Velocity** proxy (Java 25) in front of every backend.
- Static **Paper** backends (lobby, survival) and **dynamic** maps that
  scale-to-zero when idle.
- **Nakama** for friends, parties, and cross-runtime invites.
- A **World Controller** that routes players to the right backend and wakes
  sleeping worlds.
- A modded **Fantasy Forge 1.20.1** runtime behind the proxy.

## Prerequisites

- A Kubernetes cluster you can deploy to (`kubectl` works).
- `git`, `uv`, `kubectl`, and `helm` on your workstation.
- A Minecraft account to test with.

## The path

```text
1. Understand  -> reference-design/ (concepts)
2. Deploy      -> build phases (Phase 0 → 27), tracked in Implementation
3. Operate     -> guides/ (common tasks), reference-design/ (reference material)
```

## Next

- Read the [Server Setup Guide](server-setup-guide.md) for a step-by-step
  walkthrough.
- Open the [Implementation progress](../implementation/index.md) to see what is
  built and what remains.
- Browse the [Reference Design](../reference-design/index.md) to understand the
  architecture first.