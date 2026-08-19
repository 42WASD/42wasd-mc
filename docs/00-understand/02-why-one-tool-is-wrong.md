# Why "one tool solves everything" is wrong

Treating routing, world lifecycle, social state, protocol compatibility, and client mods as a single problem creates a fragile design. Here are the five traps.

## 1. A proxy is not a world orchestrator

A proxy can route a player to a backend, but it is not a Kubernetes lifecycle controller. A dynamic world requires:

```text
desired world
  → is an instance running?
  → if not, start it
  → wait until Minecraft is actually READY
  → register route
  → reserve capacity
  → transfer player / party
```

**Separation to enforce:**

```text
Velocity NetworkBridge
      → World Controller API
      → narrow Kubernetes RBAC
```

A proxy should never get unrestricted Kubernetes permissions just because it can issue `/server`.

## 2. Protocol compatibility ≠ mod compatibility

ViaVersion/ViaBackwards translate **protocol versions**. They cannot invent missing client code.

Possible: `newer Java client → ViaVersion → older Paper backend`.

Not possible: `vanilla client → proxy → Forge server requiring MineColonies + Ice and Fire`.

If a mod adds blocks, entities, registries, or client code, a proxy cannot synthesize the missing implementation.

## 3. Arbitrary community modpacks destroy stable routing

If every map picks its own loader/version, a player inside Minecraft cannot hot-replace their classpath. **Community content must target a runtime class:**

```text
vanilla-current
backrooms-current
fantasy-1.20.1-forge
experimental-horror-1
```

This is the single biggest product decision that makes everything else tractable.

## 4. A global TAB list is not a global world database

Velocity knows the **backend server**, not necessarily `map_id`, dimension, world name, party, activity, or runtime. That must be reported by the backend / control plane, then fed to TAB.

## 5. Scale-to-zero and portal switching are different paths

`mc-router` wakes sleeping StatefulSets on a **new incoming connection**. An already-connected player walking through a portal has no new public handshake. So the World Controller must handle in-game wake/readiness before Velocity transfers the player. `mc-router` stays at the edge.