# Security boundaries

## Public network boundary

Expose only:

```text
Velocity / mc-router Minecraft entry
Nakama (public client API + OAuth login) if OAuth-first sign-in is used
web UI endpoints you explicitly publish
```

Backends remain private ClusterIP services.

With OAuth-first identity, Nakama's public endpoint must be reachable so players
can complete Discord/Google OAuth. Only the OAuth/Nakama session endpoints are
public; the Minecraft backends and the Nakama admin/console stay private.

---

## Kubernetes RBAC boundary

World Controller:

```text
get/list/watch pods
get/list/watch services
get/list/watch/patch GameServerSets (game.kruise.io)
create/delete GameServerSets in the map namespace(s) it manages
```

The World Controller creates and deletes `GameServerSet`s for dynamic maps, so
`create`/`delete` are scoped to the map namespace(s) — not cluster-wide. It
scales via `patch` on `spec.replicas` (it does **not** install or delete the
OpenKruiseGame operator itself).

Avoid:

```text
cluster-admin
arbitrary Secret read
arbitrary workload exec
host access
```

---

## Proxy plugin boundary

NetworkBridge should call the World Controller.

It should **not** receive a Kubernetes admin kubeconfig.

---

## Community map boundary

A map definition is data.

A new executable plugin/mod is code.

Do not make “upload map” equivalent to “execute arbitrary jar.”

---
