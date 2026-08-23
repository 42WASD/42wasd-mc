# MapInstance schema

```json
{
  "map_id": "fantasy-kingdom-001",
  "runtime_id": "fantasy-1.20.1-forge",
  "state": "READY",
  "backend_id": "fantasy-kingdom-001",
  "service_host": "fantasy-kingdom-001.minecraft.svc.cluster.local",
  "port": 25565,
  "players": 4,
  "reservations": 1,
  "max_players": 12,
  "last_activity": "2026-08-19T...",
  "revision": 14
}
```

`state` uses the **operational (Axis-2)** vocabulary from
[routing-state-machine](../routing-state-machine/index.md): `ASLEEP`,
`STARTING`, `READY`, `STOPPING`, `ERROR`. It is the world's long-lived health,
**not** a routing-request state (`REQUESTED`/`TRANSFERRING`/`COMPLETE` belong
to a per-join operation and are not stored here).

`draining` is **not** a value of `state`. It is a separate boolean/derived flag
used while the world is otherwise `READY` (winding down for scale-to-zero). Keep
it out of the `state` enum so the five atomic operational states stay clean.

`backend_id` identifies the concrete backing workload (the `GameServerSet` name
+ ordinal). It may coincide with `map_id` for a single-instance map, but is
distinct in general — a map can be backed by multiple replicas or an Agones
`GameServer`, so `backend_id` disambiguates which instance is READY.

`last_activity` records the latest player activity or world update time. It is
the raw signal behind the `freshness` factor in `random-routing-scoring` and the
idle-drain decision (see `add-idle-sleep`).

`reservations` counts seats already promised to joining players/parties but
not yet connected; see `random-routing-scoring` and `reservations` semantics.

`revision` is an **optimistic-concurrency token** (an integer) for the *running
state*, used to guard idempotent releases if this state is persisted outside
Kubernetes. It is a different notion from the `RuntimeDefinition.revision`
(a `r1`-style **pack/runtime revision** string) and from a `MapDefinition`
revision — see [runtimedefinition-schema](../runtimedefinition-schema/index.md)
and the [world-readiness-contract](../world-readiness-contract/index.md).

