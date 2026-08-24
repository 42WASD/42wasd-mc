# RuntimeDefinition schema

`RuntimeDefinition` is a **Kubernetes custom resource** (CRD) under the
`platform.42wasd.dev/v1alpha1` API group. Git / Argo CD is the sole writer of
`RuntimeDefinition.spec`; the World Controller reads it and derives running
`MapInstance`s from it. Illustrated in YAML:

```yaml
apiVersion: platform.42wasd.dev/v1alpha1
kind: RuntimeDefinition
metadata:
  name: fantasy-1-20-1-r4
  # Kubernetes metadata.resourceVersion provides optimistic concurrency

spec:
  minecraft:
    version: "1.20.1"
    server_type: FORGE
    loader_version: "47.2.0"   # pin to the exact tested loader

  client:
    required: true
    distribution: modrinth-server-project
    project_id: "your-network-fantasy-runtime"   # Modrinth Server Project slug

  proxy:
    kind: velocity
    ambassador_required: true
    modern_forwarding: true   # must be uniform across all runtimes (proxy-wide)

  routing:
    instant_switch_within_runtime: true
    via_translation_allowed: false

  resources:
    memory: "12Gi"
    cpu_limit: "8"

  startup:
    timeout_seconds: 300

  idle:
    sleep_allowed: true
    timeout_seconds: 1200
```

> Note: `modern_forwarding` is a **network-wide** setting (Velocity serves all
> backends behind one secret). It must therefore be **the same across every
> runtime** — you cannot run some runtimes with modern forwarding and others
> without on the same proxy. Treat it as an invariant, not a per-runtime toggle.

> The `r4`-style **runtime/pack revision** in the object name (bumped on each
> pack release) is distinct from Kubernetes' built-in
> `metadata.resourceVersion`/`generation` used for optimistic concurrency. See
> [mapinstance-schema](../mapinstance-schema/index.md) and the
> [world-readiness-contract](../world-readiness-contract/index.md).

