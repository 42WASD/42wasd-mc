# Final architecture recommendation

If you want one compact answer to implement:

```text
PUBLIC ENTRY
  mc-router (optional) -> Velocity 4.0.0 / Java 25

VELOCITY
  TAB 6.1.2
  ViaVersion 5.11.0
  ViaBackwards 5.11.0
  Ambassador for Forge 1.20.1
  custom NetworkBridge

SOCIAL
  Nakama 3.40.0
  CockroachDB

DYNAMIC WORLD CONTROL
  custom World Controller
  Kubernetes StatefulSet + PVC
  itzg/minecraft-server
  mc-router edge wake
  Agones only for ephemeral sessions

CLIENT RUNTIMES
  runtime classes
  Modrinth Server Projects
  packwiz as optional Git/CI source
```

And enforce this product rule:

> **A community map may be dynamic; the required client runtime must be standardized.**

That rule is what allows portals, invites, TAB information, sleeping worlds, random Backrooms routing, and modded fantasy gameplay to coexist without turning every friend invite into dependency troubleshooting.
