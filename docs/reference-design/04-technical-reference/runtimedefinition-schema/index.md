# RuntimeDefinition schema

Illustrative:

```yaml
metadata:
  id: fantasy-1.20.1-forge
  revision: r1   # string, the pack/runtime revision (e.g. r1, r2)

minecraft:
  version: "1.20.1"
  serverType: FORGE
  loaderVersion: "47.2.0"   # pin to the exact tested loader

client:
  required: true
  distribution: modrinth-server-project
  projectId: "your-network-fantasy-runtime"   # Modrinth Server Project slug

proxy:
  kind: velocity
  ambassadorRequired: true
  modernForwarding: true   # must be uniform across all runtimes (proxy-wide)

routing:
  instantSwitchWithinRuntime: true
  viaTranslationAllowed: false

resources:
  memory: "12Gi"
  cpuLimit: "8"

startup:
  timeoutSeconds: 300

idle:
  sleepAllowed: true
  timeoutSeconds: 1200
```

> Note: `modernForwarding` is a **network-wide** setting (Velocity serves all
> backends behind one secret). It must therefore be **the same across every
> runtime** — you cannot run some runtimes with modern forwarding and others
> without on the same proxy. Treat it as an invariant, not a per-runtime toggle.

> `revision` here is the **runtime/pack revision** (a `r1`-style string, bumped on
> each pack release). This is distinct from the `MapInstance` `revision` integer,
> which is an **optimistic-concurrency token** for the running state. See
> [mapinstance-schema](../mapinstance-schema/index.md) and the
> [world-readiness-contract](../world-readiness-contract/index.md).

