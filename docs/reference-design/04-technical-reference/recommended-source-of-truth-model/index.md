# Recommended source-of-truth model

```text
Git:
  runtime definitions
  map definitions
  Kubernetes manifests
  packwiz manifests
  policy

Kubernetes:
  actual server process state
  pods
  services
  PVCs
  GameServerSet replicas

Nakama:
  user/social state
  friends
  parties
  invites
  presence
  pending joins

World Controller:
  derived live routing state
  readiness
  reservations
  lifecycle locks
```

Do not duplicate every fact into every database.

---

## Runtime and map definitions as CRDs

"Runtime definitions" and "map definitions" are not just YAML files — they are
**custom resources** (`RuntimeDefinition`, `MapDefinition`, both under a
`platform.example/v1` API group). They live in Git and are applied to the
cluster like any manifest (via Argo CD / GitOps). This is the same CRD-driven
pattern proven by operators such as Shulker (which defines
`MinecraftCluster`/`MinecraftServer` CRDs) and OpenKruiseGame.

- Declaring them as **CRDs** gives you typed validation, defaults, and a
  standard `kubectl get`/`describe` UX, and lets the World Controller watch
  them with the Kubernetes watch API.
- Git remains the source of truth for the *desired* runtime/map set; the
  World Controller turns them into *running* instances; Kubernetes reports
  the *actual* state. No custom tooling beyond a schema + controller is
  needed to "create a runtime/map definition" — the CRD + a GitOps applier is
  the mechanism.

---
