# Velocity vs Gate

## Selected default: Velocity

As of the 2026-08-19 audit:

- Velocity is actively developed; PaperMC's getting-started requires **Java 25**.
- A **4.0.0** release line exists in 2026.
- First-class goals for Paper, Sponge, Fabric, and Forge.
- Its plugin ecosystem makes TAB, ViaVersion, permissions, social bridges, and custom Java plugins far easier to assemble.

For this project "best" means: mature ecosystem, predictable operations, good docs, plugin availability, modded backend path, and easy custom extension. **Velocity wins.**

## Where Gate is genuinely stronger

Gate (Go-native) is attractive when you prioritize:

```text
small Go-native proxy/runtime
cloud-native custom engineering
Gate SDK/API control
built-in/managed ViaLite path
Java/Bedrock translation ecosystem
specific Forge FML compatibility
hostname/Lite-mode reverse proxy use cases
```

Gate's modded docs cover Forge 1.13–1.20.1. This matters because Velocity needs **Ambassador** for Forge 1.13–1.20.1.

## Why Gate is still not the default

Your requirements are not "build a proxy platform"; they are TAB, friends, invites, click-to-join, portal routing, world lifecycle, community maps, modded compatibility, and operational simplicity. Velocity's ecosystem gives a shorter path to all of those.

## Gate does not solve incompatible mod switching

```text
protocol translation != Forge registry equivalence
```

The runtime-class rule holds under Gate too.