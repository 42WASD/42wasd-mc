# Phase 3 — Deploy CockroachDB and Nakama

## 20.1 Why CockroachDB

For production Nakama in this design, follow current Nakama documentation and use CockroachDB.

Do not choose PostgreSQL merely because older/community examples are familiar.

---

## 20.2 Deploy CockroachDB

Prefer CockroachDB's current supported Helm deployment for Kubernetes.

Conceptually:

```text
CockroachDB StatefulSet
  + persistent volume
  + internal Service
  + backups
```

For a single-node homelab you may intentionally run a one-node database, but understand:

```text
one node != database high availability
```

The social service can be rebuilt; its durable database still needs backups.

---

## 20.3 Deploy Nakama 3.40.0

Pin:

```text
Nakama: 3.40.0
```

Do not use `latest` in production manifests.

Nakama needs:

```text
database address
server key
console credentials
runtime module volume, if custom server runtime is used
```

Expose Nakama internally first.

Example service intent:

```text
nakama.minecraft-system.svc.cluster.local
```

Do not expose its console publicly without authentication/network controls.

---

## 20.4 Create Minecraft identity authentication

When a player first connects through authenticated Velocity:

```text
Velocity UUID
   ↓
NetworkBridge
   ↓
Nakama custom authentication
   ↓
Nakama user
```

Use UUID as the stable custom ID.

Pseudo-flow:

```java
String minecraftUuid = player.getUniqueId().toString();

NakamaSession session =
    nakama.authenticateCustom(minecraftUuid, true, player.getUsername());
```

Store the Nakama session/token server-side, not on the vanilla Minecraft client.

---

## 20.5 First test

Acceptance criteria:

```text
[ ] player joins Velocity
[ ] NetworkBridge can authenticate/find Nakama account
[ ] reconnect returns same Nakama identity
[ ] username changes do not create new social identity
```

Do not proceed to parties until this is deterministic.

---
