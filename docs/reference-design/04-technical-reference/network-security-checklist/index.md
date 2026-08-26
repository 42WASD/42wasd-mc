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

## NetworkPolicies are GitOps-synced (Argo CD)

The games namespace is `default-deny` on ingress **and** egress. The netpols
(and the whole `clusters/alpha` overlay) are applied by Argo CD app
`tenant-games-alpha` (defined in the platform/iac repo), so the policy below
is declared in Git and re-converged automatically.

Because Kubernetes NetworkPolicies are **one-way**, each in-cluster flow needs
both an **egress** allow on the client **and** an **ingress** allow on the
destination:

| Flow | Egress (client) | Ingress (destination) |
|---|---|---|
| Nakama → CockroachDB `:26257` | `allow-games-egress` | `allow-nakama-to-cockroachdb` |
| Velocity → Paper lobby `:25565` | `allow-games-egress` | `allow-proxy-to-paper-lobby` |
| Minecraft client → Velocity `:25565` | external | `allow-games-ingress` |

> **Stale CiliumEndpoints after a node IP change:** if pods crash with
> DNS/connection timeouts after the node IP changed, the fix is not a policy
> edit — delete stale `CiliumEndpoint` CRs **and** restart the Cilium agent.
> See the iac docs `05-gitops-bootstrap/default-deny-networkpolicy` and the
> `phase-08` runbook.

---
