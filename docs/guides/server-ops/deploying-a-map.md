# Deploying a Map

How to bring a new map onto the network. The full pipeline is defined in
[Phase 27 — Community map upload pipeline](../../reference-design/03-step-by-step-implementation/community-map-upload-pipeline/index.md).

## Steps

1. **Prepare the world** — a valid Minecraft world folder, or a Modrinth pack
   for a modded map.
2. **Choose the runtime** — decide which runtime class the map needs
   (`vanilla-current`, `fantasy-1.20.1-forge`, etc.).
3. **Register map metadata** — add a map definition with its `runtimeId` to the
   World Controller (see
   [Phase 12 — map metadata](../../reference-design/03-step-by-step-implementation/define-map-metadata/index.md)).
4. **Deploy the backend** — for a static map, a StatefulSet; for a dynamic map,
   a scale-to-zero StatefulSet with a PVC.
5. **Point routing** — the proxy / controller now resolves the map to its
   backend.
6. **Validate** — run the
   [functional acceptance test](../../reference-design/04-technical-reference/functional-acceptance-test/index.md).

## Validation checklist

```text
[ ] map has a standardized runtimeId (no bespoke runtime)
[ ] world data is on a PVC (survives restart)
[ ] routing resolves the map -> backend
[ ] a compatible client can join
```

## See also

- [Dynamic world lifecycle](../../reference-design/01-understand-the-architecture-before-installing-anything/dynamic-world-lifecycle/index.md)
- [Runtime classes](../architecture/runtime-classes.md)