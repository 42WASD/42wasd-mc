# Network security checklist

Security invariants that every part of the deployment must satisfy.

## Identity & forwarding

- [ ] Backends run `online-mode=false` **only** because they're behind the proxy.
- [ ] Modern forwarding is enabled on Velocity and the secret is a Kubernetes Secret (not in Git).
- [ ] The player UUID seen by the backend equals the authenticated UUID at the proxy.

## Isolation

- [ ] Backend services are `ClusterIP` (not `LoadBalancer`/`NodePort`).
- [ ] NetworkPolicy restricts backend ingress to the proxy namespace only.
- [ ] The public endpoint only exposes Velocity / mc-router, never backends.

## Secrets & credentials

- [ ] Forwarding secret, Nakama DB password, and any API keys are stored as Kubernetes Secrets.
- [ ] No secrets committed to the repository.
- [ ] Restrict Secret access (RBAC) to the namespaces that need it.

## Runtime & supply chain

- [ ] Image tags pinned or digest-pinned before production.
- [ ] Modrinth/runtime projects are versioned and resolvable.
- [ ] Community map uploads are validated before being accepted (Step 17).

## Rate & abuse

- [ ] Login/join is rate-limited to prevent abuse.
- [ ] Wake operations are idempotent / bounded (no infinite wake loops).

## See also

- [Step 2 — Forwarding + isolation](../01-implement/step-02-forwarding-isolation.md)
- [Step 17 — Map upload](../01-implement/step-17-map-upload.md)
- [Operations: security](../03-operations/security.md)