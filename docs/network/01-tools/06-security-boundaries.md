# Security boundaries

## Public network boundary

Expose only:

```text
Velocity / mc-router Minecraft entry
Nakama only if you intentionally need a public client API
web UI endpoints you explicitly publish
```

Backends remain private ClusterIP services.

## Kubernetes RBAC boundary

World Controller should have:

```text
get/list/watch pods
get/list/watch services
get/list/watch/patch StatefulSets
optional create/delete only in map namespace if design requires it
```

Avoid:

```text
cluster-admin
arbitrary Secret read
arbitrary workload exec
host access
```

## Proxy plugin boundary

The custom NetworkBridge should call the World Controller. It should **not** receive a Kubernetes admin kubeconfig.

## Community map boundary

A map definition is **data**. A new executable plugin/mod is **code**. Do not make "upload map" equivalent to "execute arbitrary jar."