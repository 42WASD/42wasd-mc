# Verified references

The authoritative sources and component versions this guide is based on.

## Source document

The primary source of truth:

- `sources/verified_dynamic_minecraft_network_architecture_2026-08-19.md`
  (the full architecture document this site was built from)

## Verified component stack

| Component | Version | Notes |
|-----------|---------|-------|
| Velocity (proxy) | 4.0.0 | requires Java 25 |
| TAB | 6.1.2 | network-wide presence |
| ViaVersion / ViaBackwards | 5.11.0 | protocol translation |
| Nakama | 3.40.0 | social / identity |
| CockroachDB | (latest) | Nakama backing store |
| itzg/minecraft-server | 2026.8.0 | base server image |
| itzg/mc-proxy | `java25` | Velocity image |
| mc-router | latest | edge routing / wake |
| World Controller | custom | routing + runtime registry |
| Agones | optional | ephemeral fleets |
| Modrinth Server Projects | — | runtime/client packs |
| packwiz | — | optional pack tooling |

## Java requirements by runtime

- Velocity 4.x → **Java 25**
- Forge 1.20.1 (`fantasy-1.20.1-forge`) → **Java 21**
- Vanilla/Paper current → per image (`itzg` handles)

## Core rule (repeated)

> A community map may be dynamic; the required client runtime must be standardized.

## See also

- [Runtime classes](../00-understand/04-runtime-classes.md)
- [Final architecture](final-architecture.md)