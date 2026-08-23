# Build NetworkBridge for Velocity

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

## Never let the plugin directly scale Kubernetes

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

## Dynamic backend registration

When World Controller returns:

```json
{
  "state": "READY",
  "map_id": "backrooms-level-0",
  "runtime_id": "backrooms-current",
  "service_host": "backrooms-level-0.minecraft.svc.cluster.local",
  "port": 25565
}
```

These keys are the canonical `MapInstance` shape from the technical reference.

NetworkBridge can register/update the Velocity backend and then connect the player.

Pseudo-Java:

```java
ServerInfo info = new ServerInfo(
    mapId,
    new InetSocketAddress(serviceHost, port)
);

RegisteredServer server =
    proxyServer.registerServer(info);

player.createConnectionRequest(server)
      .connect();
```

Your real implementation should handle races and already-registered servers.

---
