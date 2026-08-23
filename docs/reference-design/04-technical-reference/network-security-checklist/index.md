# Network security checklist

```text
[ ] only proxy/edge is publicly exposed
[ ] backend Minecraft Services are ClusterIP
[ ] backend online-mode=false only behind proxy
[ ] Velocity modern forwarding enabled
[ ] forwarding secret stored outside Git
[ ] Forge backend uses ProxyCompatibleForge
[ ] Forge 1.20.1 route uses Ambassador
[ ] NetworkBridge does not have K8s cluster-admin
[ ] World Controller uses narrow ServiceAccount
[ ] Nakama console is private/protected
[ ] database is not public
[ ] community uploads are quarantined
[ ] arbitrary map JAR execution is denied
[ ] image versions/digests are pinned for production
```

---
