# RuntimeDefinition schema

Illustrative:

```yaml
metadata:
  id: fantasy-1.20.1-forge
  revision: r1

minecraft:
  version: "1.20.1"
  serverType: FORGE
  loaderVersion: "PIN_ME"

client:
  required: true
  distribution: modrinth-server-project
  projectId: "PIN_ME"

proxy:
  kind: velocity
  ambassadorRequired: true
  modernForwarding: true

routing:
  instantSwitchWithinRuntime: true
  viaTranslationAllowed: false

resources:
  memory: 12Gi
  cpuLimit: "8"

startup:
  timeoutSeconds: 300

idle:
  sleepAllowed: true
  timeoutSeconds: 1200
```

---
