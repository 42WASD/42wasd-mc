# Network security checklist

```text
[ ] only proxy/edge and Nakama's public client/OAuth endpoint are exposed
[ ] backend Minecraft Services are ClusterIP
[ ] backend online-mode=false only behind proxy
[ ] Velocity modern forwarding enabled
[ ] forwarding secret stored outside Git
[ ] Forge backend uses ProxyCompatibleForge
[ ] Forge 1.20.1 route uses Ambassador
[ ] NetworkBridge does not have K8s cluster-admin
[ ] World Controller uses narrow ServiceAccount
[ ] Nakama console is private/protected (only the client API is public)
[ ] database is not public
[ ] community uploads are quarantined
[ ] arbitrary map JAR execution is denied
[ ] image versions/digests are pinned for production
```

---
