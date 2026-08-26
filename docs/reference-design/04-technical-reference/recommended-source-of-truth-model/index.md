# Recommended source-of-truth model

```text
Git / Argo CD writes:
  RuntimeDefinition.spec
  MapDefinition.spec
  platform deployments (proxy, World Controller, monitoring, CRDs)
  static infrastructure

World Controller writes:
  MapInstance
  MapInstance.status
  dynamic GameServerSets (lifecycle-driven)
  reservations
  runtime operational conditions

Kubernetes / OKG writes:
  Pod status
  GameServer status
  GameServerSet status
  PVC state

Nakama:
  user/social state
  friends
  parties
  invites
  presence
  pending joins
```

Do not duplicate every fact into every database.

---

## Single-writer rule

Every resource field has **exactly one writer**. This is what makes a GitOps
setup safe: if both the World Controller and Argo CD wrote
`GameServerSet.spec.replicas`, they could fight (World Controller → 0, Argo CD
→ 1 a moment later). Decide the owner up front and never have two writers
patch the same field.

- **Git / Argo CD** owns the *declared* definition fields
  (`RuntimeDefinition.spec`, `MapDefinition.spec`) and static platform
  manifests.
- **World Controller** owns `MapInstance` (created/updated/destroyed), dynamic
  `GameServerSet` **replicas** for named persistent worlds, reservations, and
  operational conditions.
- **Kubernetes / OKG** owns `Pod`/`GameServer`/`GameServerSet` status and PVC
  state.
- **Nakama** owns social/presence/invite records.

### Replica owner rule

There is exactly **one replica owner per workload**:

```text
NAMED PERSISTENT WORLD
  MapDefinition
       ↓
  World Controller          ← sole replica owner (0↔1)
       ↓
  GameServerSet (replicas 0/1)
       ↓
  PVC
  NO KEDA ScaledObject for this GameServerSet
```

```text
POOLED CAPACITY (warm pool / ephemeral fleet)
  KEDA / external scaler    ← sole replica owner (0..N)
       ↓
  GameServerSet
  World Controller allocates/reserves servers but DOES NOT patch replicas
```

The World Controller drives the 0↔1 edge for named worlds itself (via the
GameServerSet `/scale` subresource); KEDA is used only for pooled workloads it
does not own. This is a **formal invariant**: never attach a KEDA
`ScaledObject` to a `GameServerSet` whose replicas the World Controller owns,
and never let the World Controller patch replicas of a pooled GameServerSet
that KEDA owns.

---

## Runtime and map definitions as CRDs

"Runtime definitions" and "map definitions" are not just YAML files — they are
**custom resources** (`RuntimeDefinition`, `MapDefinition`, `MapInstance`,
all under the **`platform.42wasd.dev/v1alpha1`** API group). They live in Git
and are applied to the cluster like any manifest (via Argo CD / GitOps). This
is the same CRD-driven pattern proven by operators such as Shulker (which
defines `MinecraftCluster`/`MinecraftServer` CRDs) and OpenKruiseGame.

- Declaring them as **CRDs** gives you typed validation, defaults, and a
  standard `kubectl get`/`describe` UX, and lets the World Controller watch
  them with the Kubernetes watch API.
- Git remains the source of truth for the *desired* runtime/map set; the
  World Controller turns them into *running* instances; Kubernetes reports
  the *actual* state. No custom tooling beyond a schema + controller is
  needed to "create a runtime/map definition" — the CRD + a GitOps applier is
  the mechanism.

---

## NetworkPolicies and the games namespace are Argo-owned

The static networking in `prd-games-42wasd-admin` — the `NetworkPolicy` set
and the CockroachDB backing store — has **exactly one writer: Argo CD**
(app `tenant-games-alpha`, defined in the platform repo, syncing this repo's
`clusters/alpha`). Never patch these by hand; if they drift, fix Git and let
Argo `selfHeal` converge them.

- `clusters/alpha/networkpolicy.yaml` — the games netpols
  (`allow-games-egress`, `allow-games-ingress`, `allow-proxy-to-paper-lobby`,
  `allow-nakama-to-cockroachdb`).
- `clusters/alpha/cockroachdb/` — CockroachDB StatefulSet + Services + cert
  rotation CronJobs (migrated from Helm so Argo owns it).

The `prd-games-42wasd-admin` Namespace itself is owned by the platform
`platform-namespaces` app, not here.

---
