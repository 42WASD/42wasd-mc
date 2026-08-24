# Final architecture recommendation

If you want one compact answer to implement:

```text
PUBLIC ENTRY
  itzg/mc-proxy (java25 variant) -> Velocity 4.0.0 / Java 25
  mc-router (optional) edge wake

VELOCITY
  TAB 6.1.2
  ViaVersion 5.11.0
  ViaBackwards 5.11.0
  Ambassador + ProxyCompatibleForge for Forge 1.20.1
  custom NetworkBridge

SOCIAL
  Nakama 3.40.0 (OAuth-first identity: Discord/Google login)
  CockroachDB

DYNAMIC WORLD CONTROL
  custom World Controller (sole replica owner for named persistent worlds)
  OpenKruiseGame GameServerSet + PVC
  itzg/minecraft-server
  itzg/mc-monitor (readiness/reachability probe; TPS/GC from backend telemetry + spark)
  KEDA (optional) pooled-only scale owner — NOT on named worlds
  Velero (optional) PVC backup/restore (restore drills = our runbook/CI)
  mc-router edge wake (webhook -> World Controller for GameServerSet)
  Agones only for ephemeral sessions

CLIENT RUNTIMES
  runtime classes
  Modrinth Server Projects
  AstralRinth (Modrinth-based launcher fork: Microsoft, Ely.by, OAuth Device, offline for local/testing)
  packwiz as optional Git/CI source
```

And enforce this product rule:

> **A community map may be dynamic; the required client runtime must be standardized.**

That rule is what allows portals, invites, TAB information, sleeping worlds, random Backrooms routing, and modded fantasy gameplay to coexist without turning every friend invite into dependency troubleshooting.
