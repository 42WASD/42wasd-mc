# Phase 12 — Build NetworkBridge

This is the glue plugin for Velocity.

## Responsibilities

```text
authenticate Minecraft UUID with Nakama
implement /worlds
implement /join
implement /invite
implement /party
call World Controller
register dynamic backend routes
connect player after readiness
publish MiniPlaceholders
maintain presence
```

## Never let the plugin directly scale Kubernetes

**Bad:**

```text
Velocity plugin -> cluster-admin kubeconfig
```

**Good:**

```text
Velocity plugin -> mTLS/internal HTTP -> World Controller -> narrow RBAC
```

## Dynamic backend registration

When the World Controller returns:

```json
{
  "server_id": "backrooms-level-0",
  "host": "backrooms-level-0.minecraft.svc.cluster.local",
  "port": 25565
}
```

NetworkBridge can register/update the Velocity backend and then connect the player:

```java
ServerInfo info = new ServerInfo(
    serverId,
    new InetSocketAddress(host, port)
);

RegisteredServer server = proxyServer.registerServer(info);

player.createConnectionRequest(server).connect();
```

Handle races and already-registered servers.