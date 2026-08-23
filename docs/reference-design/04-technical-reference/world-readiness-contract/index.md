# World readiness contract

World Controller returns READY only when:

```text
StatefulSet desired replicas >= 1
Pod Ready
Service endpoints exist
Minecraft status check succeeds
runtime revision matches expected revision
server is not draining
capacity reservation is available
```

This contract is more useful than a generic `/healthz`.

---
