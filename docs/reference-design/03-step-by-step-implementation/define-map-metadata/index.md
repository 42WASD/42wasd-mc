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
guard; the `world.pvc` value is what maps to the GameServerSet instance name.

---
