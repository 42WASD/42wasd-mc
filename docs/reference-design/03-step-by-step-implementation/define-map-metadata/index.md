# Define map metadata

Example (canonical shape matches the `MapInstance` naming convention in the
technical reference — flat top-level keys, snake_case):

```yaml
apiVersion: platform.example/v1
kind: MapDefinition

metadata:
  id: backrooms-level-0
  display_name: "Backrooms — Level 0"
  creator_id: "user-123"

runtime_id: backrooms-current
enabled: true

persistence: persistent

capacity:
  max_players: 12

routing:
  public: true
  random_eligible: true
  allow_party_join: true
  weight: 1.0

tags:
  - horror
  - backrooms
  - community

world:
  pvc: backrooms-level-0-world

idle:
  sleep_after_seconds: 600
```

Separate:

```text
MapDefinition = what the world is
MapInstance   = current running state
```

The `enabled` field is the source of the World Controller's `map_def.enabled`
guard.

### Naming convention

Kubernetes StatefulSet/OKG instances and PVCs are named independently:

```text
GameServerSet instance name  = <map_id>            (the running unit the World Controller scales)
PVC / volume claim           = <map_id>-world      (the durable world data)
```

So a map with `id: backrooms-level-0` gets:

```text
GameServerSet name:  backrooms-level-0
Service name:        backrooms-level-0
PVC / claim:         backrooms-level-0-world
```

The **GameServerSet instance name always equals the `map_id`** — the World
Controller's `ensure-ready` looks up the GameServerSet by `map_id`
(`instance_name == map_id`). The PVC is a separate resource whose name is
`<map_id>-world`; the instance and its volume are not the same resource, so
keep their names distinct. `world.pvc` records the PVC/claim name; the
GameServerSet name is derived from `map_id`, not from `world.pvc`.

