# Adding a Backend

How to register a new backend (static or dynamic) with the World Controller so
the proxy can route to it.

## Static backend (always running)

1. Deploy a StatefulSet (e.g. a Paper lobby) with a stable logical ID.
2. Create a `ClusterIP` Service (never `LoadBalancer`).
3. Register the backend with the World Controller.
4. Add a network policy so only the proxy can reach it.

## Dynamic backend (scale-to-zero)

1. Deploy a scale-to-zero StatefulSet with a PVC for world data.
2. Register the map in the World Controller with its `runtimeId`.
3. The controller will scale `0 → 1` on wake, and back to `0` when idle.

## Fantasy / modded runtime

- A Forge runtime needs the Ambassador + ProxyCompatibleForge so modern
  forwarding works behind Velocity. See
  [Phase 8 — Deploy the Forge runtime](../../reference-design/build/03-step-by-step-implementation/08-25-phase-8-deploy-the-forge-1-20-1-fantasy-runtime/index.md).

## Validation

```text
[ ] backend is reachable only via the proxy (ClusterIP + network policy)
[ ] World Controller resolves the backend for the map
[ ] a compatible client can be routed there
```

## See also

- [Phase 12 — NetworkBridge](../../reference-design/build/03-step-by-step-implementation/12-29-phase-12-build-networkbridge-for-velocity/index.md)
- [Runtime classes](../architecture/runtime-classes.md)