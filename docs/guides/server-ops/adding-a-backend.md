# Adding a Backend

How to register a new backend (static or dynamic) with the World Controller so
the proxy can route to it.

## Static backend (always running)

1. Deploy a GameServerSet (e.g. a Paper lobby) with a stable logical ID.
2. Create a `ClusterIP` Service (never `LoadBalancer`).
3. Register the backend with the World Controller.
4. Add a network policy so only the proxy can reach it.

## Dynamic backend (scale-to-zero)

1. Deploy a scale-to-zero GameServerSet with a PVC for world data.
2. Register the map in the World Controller with its `runtime_id`.
3. The controller will scale `0 → 1` on wake, and back to `0` when idle.

## Fantasy / modded runtime

- A Forge runtime needs the Ambassador + ProxyCompatibleForge so modern
  forwarding works behind Velocity. See
  [Phase 10 — Deploy the Forge runtime](../../reference-design/03-step-by-step-implementation/deploy-the-forge-1-20-1-fantasy-runtime/index.md).

## Validation

```text
[ ] backend is reachable only via the proxy (ClusterIP + network policy)
[ ] World Controller resolves the backend for the map
[ ] a compatible client can be routed there
```

## See also

- [Phase 14 — NetworkBridge](../../reference-design/03-step-by-step-implementation/build-networkbridge-for-velocity/index.md)
- [Runtime classes](../architecture/runtime-classes.md)