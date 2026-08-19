# Security

Ongoing security operations and hardening for the running network.

## Recurring checks

- **Re-verify forwarding** after any proxy/backend upgrade (backends reachable?).
- **Scan images** for known-vulnerable base images (Java bases especially).
- **Review NetworkPolicies** whenever a backend is added.
- **Rotate secrets** (forwarding secret, DB creds) on a schedule and after any exposure.

## Hardening checklist

- [ ] Only the proxy/router exposed; backends `ClusterIP`.
- [ ] NetworkPolicy limited to proxy → backend.
- [ ] Secrets in Kubernetes Secrets, not committed.
- [ ] Rate-limit login/join to curb abuse.
- [ ] Runtime/pack pinned (Step 14), no untracked mods.
- [ ] Map uploads validated (Step 17) before being made available.

## Incidents

- If a backend is exposed accidentally, assume the worst: rotate the forwarding secret, disconnect players, review logs.

## See also

- [Security checklist](../02-reference/security-checklist.md)
- [Step 2 — Forwarding + isolation](../01-implement/step-02-forwarding-isolation.md)
- [Backups](backups.md)