# Define the runtime catalog

Create `runtimes/<id>/runtime.yaml`.

Example (canonical shape matches the `RuntimeDefinition` schema in the
technical reference — `04-technical-reference/runtimedefinition-schema`):

```yaml
apiVersion: platform.example/v1
kind: RuntimeDefinition
metadata:
  id: backrooms-current

minecraft:
  serverType: PAPER
  version: "PIN_TESTED_VERSION"

client:
  required: false
  distribution: modrinth-server-project

proxy:
  kind: velocity
  ambassadorRequired: false
  modernForwarding: true   # must be uniform across all runtimes

routing:
  instantSwitchWithinRuntime: true
  viaTranslationAllowed: true

resources:
  memory: "2Gi"
  cpuLimit: "4"

startup:
  timeoutSeconds: 300

idle:
  sleepAllowed: true
  timeoutSeconds: 1200
```

Content policy (world uploads, plugins-from-map, client mods-from-map) is a
separate concern enforced by the World Controller and the security boundary,
not a field on the runtime definition.

This does not have to be a Kubernetes CRD initially.

It can be your own YAML schema consumed by the World Controller.

Start simple.

---
