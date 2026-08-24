# Capability cheat sheet

| Component | Proxy routing | Social | Dynamic K8s lifecycle | Protocol versions | Client mod install | Persistent world storage |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| Velocity | ✅ | plugin layer | ❌ | plugin layer | ❌ | ❌ |
| Gate classic | ✅ | custom/API layer | ❌ | ✅ ViaLite path | ❌ | ❌ |
| TAB | ❌ | display only | ❌ | ❌ | ❌ | ❌ |
| ViaVersion/Backwards | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| Nakama | ❌ MC routing | ✅ | ❌ | ❌ | ❌ | metadata only |
| mc-router | hostname edge routing | ❌ | ✅ edge wake (webhook; native 0↔1 is StatefulSet-only) | ❌ | ❌ | ❌ |
| World Controller | policy decision | integrates | ✅ | compatibility metadata | launcher link selection | coordinates GameServerSet + PVC workload |
| itzg/minecraft-server | ❌ | ❌ | runs inside K8s | server-specific | server-side pack install | with PVC |
| Agones | connection allocation | ❌ | ✅ ephemeral/session model | ❌ | ❌ | not the default persistence model |
| Modrinth Server Projects | ❌ | ❌ | ❌ | selects correct runtime | ✅ | ❌ |
| packwiz | ❌ | ❌ | ❌ | pack definition | ✅ pre-launch/update workflow | ❌ |
| OpenKruiseGame GameServerSet | ❌ | ❌ | ✅ stateful game workload, scale-to-zero | ❌ | ❌ | ✅ in-place update + PVC |
| itzg/mc-proxy | ❌ | ❌ | runs inside K8s | proxy JVM | ❌ | ❌ |
| CockroachDB | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ (Nakama persistence) |
| AstralRinth | ❌ | ❌ | ❌ | client runtime | ✅ launcher installs | ❌ |
| itzg/mc-monitor | ❌ | ❌ | ❌ | ❌ | ❌ | readiness/reachability probe (status/ping, online count, latency) — not TPS/GC |
| KEDA | ❌ | ❌ | ✅ pooled-capacity 0↔1 scale owner only | ❌ | ❌ | ❌ |
| Velero | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ PVC backup/restore (restore drills are our runbook/CI) |

> **Replica-owner note:** the World Controller is the **sole replica owner** for
> named persistent worlds (their `GameServerSet` gets **no** KEDA
> `ScaledObject`). KEDA owns replicas only for **pooled** capacity the World
> Controller does not own. See
> [recommended-source-of-truth-model](../../04-technical-reference/recommended-source-of-truth-model/index.md).

The boundaries are deliberate.

> **Identity note:** Nakama is also the **OAuth-first identity anchor** (Discord/Google
> social login). It owns the canonical user account and session; the Minecraft UUID is a
> linked runtime binding, not the identity anchor.

---
