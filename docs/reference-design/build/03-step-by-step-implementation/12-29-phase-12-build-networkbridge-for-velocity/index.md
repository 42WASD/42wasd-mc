# Phase 12 — Build NetworkBridge for Velocity

This is the glue plugin.

Responsibilities:

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

---

## 29.1 Never let the plugin directly scale Kubernetes

Bad:

```text
Velocity plugin
  -> cluster-admin kubeconfig
```

Good:

```text
Velocity plugin
  -> mTLS/internal HTTP
  -> World Controller
  -> narrow RBAC
```

---

## 29.2 Dynamic backend registration

When World Controller returns:

```json
{
  "server_id": "backrooms-level-0",
  "host": "backrooms-level-0.minecraft.svc.cluster.local",
  "port": 25565
}
```

NetworkBridge can register/update the Velocity backend and then connect the player.

Pseudo-Java:

```java
ServerInfo info = new ServerInfo(
    serverId,
    new InetSocketAddress(host, port)
);

RegisteredServer server =
    proxyServer.registerServer(info);

player.createConnectionRequest(server)
      .connect();
```

Your real implementation should handle races and already-registered servers.

---
