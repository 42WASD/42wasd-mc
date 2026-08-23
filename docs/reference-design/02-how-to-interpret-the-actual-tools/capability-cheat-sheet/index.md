# Capability cheat sheet

| Component | Proxy routing | Social | Dynamic K8s lifecycle | Protocol versions | Client mod install | Persistent world storage |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| Velocity | ✅ | plugin layer | ❌ | plugin layer | ❌ | ❌ |
| Gate classic | ✅ | custom/API layer | ❌ | ✅ ViaLite path | ❌ | ❌ |
| TAB | ❌ | display only | ❌ | ❌ | ❌ | ❌ |
| ViaVersion/Backwards | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| Nakama | ❌ MC routing | ✅ | external integration | ❌ | ❌ | metadata only |
| mc-router | hostname edge routing | ❌ | ✅ limited 0↔1 GameServerSet wake | ❌ | ❌ | ❌ |
| World Controller | policy decision | integrates | ✅ | compatibility metadata | launcher link selection | coordinates GameServerSet + PVC workload |
| itzg/minecraft-server | ❌ | ❌ | runs inside K8s | server-specific | server-side pack install | with PVC |
| Agones | connection allocation | ❌ | ✅ ephemeral/session model | ❌ | ❌ | not the default persistence model |
| Modrinth Server Projects | ❌ | ❌ | ❌ | selects correct runtime | ✅ | ❌ |
| packwiz | ❌ | ❌ | ❌ | pack definition | ✅ pre-launch/update workflow | ❌ |

The boundaries are deliberate.

> **Identity note:** Nakama is also the **OAuth-first identity anchor** (Discord/Google
> social login). It owns the canonical user account and session; the Minecraft UUID is a
> linked runtime binding, not the identity anchor.

---
