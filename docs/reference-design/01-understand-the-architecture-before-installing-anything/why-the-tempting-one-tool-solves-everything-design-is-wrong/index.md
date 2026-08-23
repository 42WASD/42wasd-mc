# Why the tempting “one tool solves everything” design is wrong

## Problem 1 — A proxy is not a world orchestrator

Velocity and Gate can route a connected player to a backend, but they are not by themselves a Kubernetes lifecycle controller.

A dynamic world requires:

```text
desired world
    ↓
is an instance already running?
    ↓
if not: start it
    ↓
wait until Minecraft is actually READY
    ↓
register route
    ↓
reserve capacity
    ↓
transfer player / party
```

A proxy should not be given unrestricted Kubernetes permissions merely because it can issue a `/server` command.

The better separation is:

```text
Velocity NetworkBridge
      ↓
World Controller API
      ↓
narrow Kubernetes RBAC
```

---

## Problem 2 — Minecraft protocol compatibility is not mod compatibility

A protocol translator such as ViaVersion/ViaBackwards, or Gate's ViaLite integration, can translate **Minecraft network protocol versions**.

It cannot invent missing client code.

This may be possible:

```text
newer Java client
    ↓
ViaVersion
    ↓
older Paper backend
```

This is fundamentally different:

```text
vanilla client
    ↓
proxy
    ↓
Forge server requiring MineColonies + Ice and Fire
```

The second case requires the correct loader/mod set on the client.

If a mod adds blocks, entities, registries, screens, packet types, recipes, animations, or required client code, a proxy cannot synthesize the missing implementation.

---

## Problem 3 — Arbitrary community modpacks destroy seamless switching

Imagine allowing every map author to choose anything:

```text
Map A -> 1.21.x Paper
Map B -> 1.20.1 Forge + 145 mods
Map C -> 1.21.x NeoForge + 80 different mods
Map D -> 1.19.2 Fabric
Map E -> another incompatible Forge registry
```

A player already inside Minecraft cannot continuously hot-replace the loader, game version, and Java classpath.

Therefore community content should target **runtime classes**.

Example:

```text
vanilla-current
backrooms-current
fantasy-1.20.1-forge
experimental-horror-1
```

A community creator chooses a runtime class and supplies compatible world/content data.

This is the single biggest product decision that makes the rest of the architecture tractable.

---

## Problem 4 — A global TAB list is not automatically a global world database

Velocity knows which **backend server** a player is connected to.

It does not necessarily know:

```text
map_id
dimension
exact world name
party
current activity
runtime class
```

That information must be reported from the backend or maintained by the network control plane.

The correct flow is:

```text
Paper/Forge bridge
    ↓ player world/dimension changed
World Controller / Nakama presence
    ↓
NetworkBridge placeholder
    ↓
TAB on Velocity
```

---

## Problem 5 — Scale-to-zero and portal switching are two different traffic paths

`mc-router` can see a new incoming connection to a hostname and can wake a Kubernetes StatefulSet before forwarding the connection.

But consider an already-connected player:

```text
Player is already connected to Velocity
    ↓
walks into portal
    ↓
Velocity wants to switch backend
```

There is no new public TCP handshake entering `mc-router`.

Therefore, for **in-game server switching**, your World Controller must perform the wake/readiness operation before Velocity transfers the player.

`mc-router` is still useful at the network edge; it is not the complete in-game world lifecycle controller.

---
