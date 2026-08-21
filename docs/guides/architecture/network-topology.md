# Network Topology

A compact view of how a player reaches a backend, including the wake path for
sleeping worlds. The full state machine is in the
[Reference Design](../../reference-design/index.md).

## Logical layers

```text
Player
  -> mc-router (public edge)
  -> Velocity (proxy, modern forwarding)
  -> World Controller (route decision)
       -> static backend (lobby / survival)   [always running]
       -> dynamic world (scale-to-zero)        [woken on demand]
       -> fantasy runtime (Forge 1.20.1)       [requires Ambassador]
```

## Two traffic paths

- **Join / join a friend** — the proxy routes directly to the target backend.
- **Portal / random / wake** — the proxy consults the World Controller, which
  may scale a sleeping world to `1` before transferring the player.

## See also

- [Dynamic world lifecycle](../../reference-design/background/01-understand-the-architecture-before-installing-anything/08-8-dynamic-world-lifecycle/index.md)
- [World Controller](../../reference-design/build/03-step-by-step-implementation/11-28-phase-11-build-the-world-controller/index.md)