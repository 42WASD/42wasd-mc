# Create Kubernetes namespaces

The generic design assumes `minecraft` (game servers) / `minecraft-system`
(proxy, world-controller, NetworkBridge, mc-router, CockroachDB, Nakama).
This cluster already has **tenant-specific namespace policy**, so we adapt it
rather than bypassing it (per the design's own instruction).

## Decisions (locked in Phase 0)

| Layer | Name |
|-------|------|
| Cluster (kube context) | `alpha-games-prd` |
| Production games namespace | `prd-games-42wasd-admin` |
| Dev mirror | `dev-games-42wasd-admin` |

The `minecraft` / `minecraft-system` split is **not created**. Everything
deploys into `prd-games-42wasd-admin` (and its `dev-` mirror).

## Why one shared namespace (research-grounded)

Kubernetes guidance is explicit that namespaces are for **team / project /
tenant boundaries**, not for separating slightly different versions of the same
software — and to *start* using namespaces only when you need the features
they provide (RBAC, quotas, NetworkPolicies). Argo CD guidance likewise offers
**ApplicationSets** for hosting multiple apps/games within one namespace.

For this platform:

1. **Env boundary = namespace.** `prd-games-42wasd-admin` vs
   `dev-games-42wasd-admin` is the one real seam (prod must not mix with
   ephemeral dev) and it already exists.
2. **Shared platform must NOT be per-game.** Velocity, the lobby, World
   Controller, NetworkBridge, CockroachDB, and Nakama are network-wide and
   shared by every game/world. Re-creating them per game (or per namespace)
   would fragment the shared backends and complicate proxy routing.
3. **Game/world boundary = labels + Argo CD Applications, not namespaces.**
   All games share the same platform, so they live in the single games
   namespace, distinguished by labels (e.g. `game=...`, `role=world`,
   `role=proxy`) and by label-scoped Argo CD `Application`s / `ApplicationSet`s.
   "Add a new game" = add one Application + labels, not a whole namespace,
   RBAC, and quotas.

### When we WOULD add a new namespace later

Only on a real boundary:

- a second team needing its own RBAC / quota / NetworkPolicy (true multitenancy);
- a game needing aggressive resource isolation (its own `ResourceQuota`);
- regulatory / data-segregation requirements.

For a single-admin homelab/self-hosted operation these do not apply today.

## Apply

```bash
kubectl apply -f clusters/alpha/namespace.yaml
```

The manifest at `clusters/alpha/namespace.yaml` declares the games namespace
with the `environment: prd` and `app.kubernetes.io/managed-by: gitops` labels.
On the live cluster `prd-games-42wasd-admin` already exists (Active); the
manifest is the declarative source of truth so GitOps can reconcile it.

---
