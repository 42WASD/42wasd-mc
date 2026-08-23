# Runtime Classes

A **runtime class** defines exactly what a player's client must run to join a
map. The core rule of this architecture:

> A community map may be dynamic; the required client runtime must be
> standardized.

## The standard runtimes

| Runtime ID | Client | Notes |
|-----------|--------|-------|
| `vanilla-current` | vanilla (current) | the default, no mods |
| `backrooms-current` | vanilla (current) | same runtime, different content |
| `fantasy-1.20.1-forge` | Forge 1.20.1 + mods | modded, via Ambassador |
| `experimental-*` | varying | not stable, off by default |

## Why it matters

- Routing, invites, and the random portal all check a player's runtime before
  transferring them.
- A vanilla player is never sent to a `fantasy` map; a Forge player can be.
- Protocol translation (ViaVersion) handles version drift, but **not** mod
  incompatibility — that is exactly why runtimes are standardized.

## See also

- [Runtime classes (concept)](../../reference-design/01-understand-the-architecture-before-installing-anything/runtime-classes-the-rule-that-makes-seamless-ux-possible/index.md)
- [RuntimeDefinition schema](../../reference-design/04-technical-reference/runtimedefinition-schema/index.md)