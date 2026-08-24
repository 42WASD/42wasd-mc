# Define the runtime catalog

Create `runtimes/<id>/runtime.yaml`.

Example (canonical shape matches the `RuntimeDefinition` schema in the
technical reference — `04-technical-reference/runtimedefinition-schema`):

```yaml
apiVersion: platform.42wasd.dev/v1alpha1
kind: RuntimeDefinition
metadata:
  id: backrooms-current

minecraft:
  server_type: PAPER
  version: "PIN_TESTED_VERSION"
  java: 21

client:
  required: false
  distribution: modrinth-server-project

proxy:
  kind: velocity
  ambassador_required: false
  modern_forwarding: true   # must be uniform across all runtimes

routing:
  instant_switch_within_runtime: true

protocol_compatibility:
  - client: "1.21.11"
    status: VERIFIED
  - client: "26.1"
    status: VERIFIED

resources:
  memory: "2Gi"
  cpu_limit: "4"

startup:
  timeout_seconds: 300

idle:
  sleep_allowed: true
  timeout_seconds: 1200
```

Content policy (world uploads, plugins-from-map, client mods-from-map) is a
separate concern enforced by the World Controller and the security boundary,
not a field on the runtime definition.

This does not have to be a Kubernetes CRD initially.

It can be your own YAML schema consumed by the World Controller.

Start simple.

---
