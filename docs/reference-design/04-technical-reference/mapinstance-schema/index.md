# MapInstance schema

`MapInstance` is a **Kubernetes custom resource** (CRD), not an arbitrary JSON
record. It lives under the `platform.42wasd.dev/v1alpha1` API group. The World
Controller is the sole writer of `MapInstance` (its `spec` comes from a
`MapDefinition`; its `status` is maintained by the controller). Example:

```yaml
apiVersion: platform.42wasd.dev/v1alpha1
kind: MapInstance
metadata:
  name: fantasy-kingdom-001
  # Kubernetes supplies resourceVersion / generation for optimistic concurrency

spec:
  mapRef: fantasy-kingdom
  runtimeRef: fantasy-1-20-1-r4

status:
  phase: Ready               # operational (Axis-2) phase
  workloadRef:
    apiVersion: game.kruise.io/v1alpha1
    kind: GameServerSet
    name: fantasy-kingdom-001
  endpoint:
    host: fantasy-kingdom-001.minecraft.svc.cluster.local
    port: 25565
  players: 4
  reservations: 1
  runtimeRevision: r4
  conditions:
    - type: KubernetesReady
      status: "True"
    - type: MinecraftReachable
      status: "True"
    - type: RuntimeRevisionMatched
      status: "True"
    - type: AcceptingPlayers
      status: "True"
  observedGeneration: 12
```

## Key decisions

- **`status.phase`** uses the **operational (Axis-2)** vocabulary from
  [routing-state-machine](../routing-state-machine/index.md): `ASLEEP`,
  `STARTING`, `READY`, `STOPPING`, `ERROR`. It is the world's long-lived
  health, **not** a routing-request state (`REQUESTED`/`TRANSFERRING`/
  `COMPLETE` belong to a per-join operation and are not stored here).
- **`draining` is not a value of `status.phase`.** It is a separate boolean or
  condition used while the world is otherwise `READY` (winding down for
  scale-to-zero). Keep it out of the phase enum so the five atomic operational
  states stay clean.
- **`spec.workloadRef`** identifies the concrete backing workload (the
  `GameServerSet` name + ordinal). It may point at a single instance for a
  single-instance map, or an Agones `GameServer` in general.
- **`status.conditions`** carries structured readiness state
  (`KubernetesReady`, `MinecraftReachable`, `RuntimeRevisionMatched`,
  `AcceptingPlayers`) and is the place to add future checks rather than
  inventing more phase values. Prefer **conditions** over an ever-expanding
  phase enum (`STARTING_MINECRAFT`, `STARTING_NETWORK`, `STARTING_RUNTIME`,
  `WAITING_PLUGIN`, ...). Keep the high-level `status.phase` state machine
  (`ASLEEP`/`STARTING`/`READY`/`STOPPING`/`ERROR`) and use conditions to tell
  operators *why* an instance is not yet joinable.
- **No home-grown integer revision.** Instead of a custom
  `revision: 14` concurrency token, rely on Kubernetes' built-in
  `metadata.resourceVersion` / `metadata.generation` + `status.observedGeneration`
  for optimistic concurrency. `runtimeRevision` (a `r4`-style **pack/runtime
  revision** string) is a *different* notion — it records which runtime pack
  revision this instance is pinned to (see
  [runtimedefinition-schema](../runtimedefinition-schema/index.md)).

## Source-of-truth notes

Ownership is split so there is exactly **one writer per resource**, the same
principle as replica ownership:

```text
GIT / ARGO CD
  RuntimeDefinition.spec
  MapDefinition.spec
  platform deployments / static configuration

WORLD CONTROLLER
  MapInstance (create/update/destroy)
  MapInstance.spec
  dynamic GameServerSet creation
  reservations / routing state

KUBERNETES / OPENKRUISEGAME
  Pod status
  GameServer status
  GameServerSet status
  PVC status
```

Do **not** put live `MapInstance` resources under GitOps reconciliation: the
World Controller owns them dynamically, so Argo CD would otherwise compete as a
second writer and recreate the multiple-writer problem.

- The World Controller creates/updates/destroys `MapInstance` and owns its
  `status`.
- Kubernetes/OKG owns `Pod`/`GameServerSet`/`GameServer` status and PVC state.
- `status.players`, `status.reservations`, and `status.conditions` are derived
  from mc-monitor reachability + World Controller reservation state + backend
  telemetry (see [world-readiness-contract](../world-readiness-contract/index.md)
  and [random-routing-scoring](../random-routing-scoring/index.md)).

