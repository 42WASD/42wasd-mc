# Source-of-truth model

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
  StatefulSet replicas

Nakama:
  user/social state
  friends
  parties
  invites
  presence
  pending invites

World Controller:
  derived live routing state
  readiness
  reservations
  lifecycle locks
```

Do not duplicate every fact into every database.