# Phase 9 — Define the runtime catalog

Create `runtimes/<id>/runtime.yaml`.

Example:

```yaml
apiVersion: platform.example/v1
kind: RuntimeDefinition
metadata:
  id: backrooms-current

spec:
  minecraft:
    serverType: PAPER
    version: "PIN_TESTED_VERSION"

  client:
    modpackRequired: false
    resourcePackRequired: true

  routing:
    viaCompatible: true
    randomPoolEligible: true

  contentPolicy:
    allowWorldUpload: true
    allowPluginsFromMap: false
    allowClientModsFromMap: false

  resources:
    requests:
      cpu: "1"
      memory: "2Gi"
    limits:
      cpu: "4"
      memory: "6Gi"
```

This does not have to be a Kubernetes CRD initially.

It can be your own YAML schema consumed by the World Controller.

Start simple.

---
