# RuntimeDefinition schema

Illustrative:

```yaml
metadata:
  id: fantasy-1.20.1-forge
  revision: r1

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
