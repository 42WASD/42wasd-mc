# Proxy decision: Velocity vs Gate

## Selected default: Velocity

As of the 2026-08 audit:

- Velocity remains actively developed.
- PaperMC's getting-started docs require **Java 25**.
- The repository shows a **4.0.0** release in 2026.
- First-class support goals for Paper, Sponge, Fabric and Forge.
- Its ecosystem makes TAB, ViaVersion, permissions, social bridges, and custom Java plugins easier to assemble.

For this project, "best" means:

```text
mature ecosystem
predictable operational model
good documentation
plugin availability
modded backend path
easy custom extension
```

That makes Velocity the better default than Gate.

## Where Gate is genuinely stronger

Gate is attractive when you prioritize:

```text
small Go-native proxy/runtime
cloud-native custom engineering
Gate SDK/API control
built-in/managed ViaLite path
built-in Gate ecosystem for Java/Bedrock translation
specific Forge FML compatibility behavior
hostname/Lite-mode reverse proxy use cases
```

Gate's modded-server documentation explicitly covers Forge 1.13–1.20.1. This matters for the fantasy runtime because Velocity itself needs Ambassador for Forge 1.13–1.20.1.

## Why Gate is still not the default

The requirements are not primarily "build a proxy platform." They are:

```text
TAB
friends
party invites
click-to-join
portal routing
world lifecycle
community maps
modded compatibility
operational simplicity
```

Velocity's ecosystem gives a shorter path to those product features. Gate becomes more compelling if you later decide to make the network proxy itself a custom cloud-native component.

## Gate does not solve incompatible mod switching

Even with Gate's managed Java-version translation:

```text
protocol translation != Forge registry equivalence
```

Switching between modded backends is only safe when the client and server-side mod/registry expectations are compatible. **The runtime-class rule remains required under Gate too.**