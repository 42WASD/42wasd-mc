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

## 20.4 Create identity authentication (OAuth-first)

The canonical identity is the **Nakama account created via Discord/Google OAuth**
(see page 07). This is what prevents abuse from anonymous users and removes the
need to build your own user management. The offline Minecraft UUID is only a
runtime binding, never the identity anchor.

Flow when a player first connects through Velocity:

```text
Discord/Google OAuth (browser or launcher)
   ↓
Nakama social-provider authentication (authenticateGoogle / authenticateApple
   or a custom OAuth provider for Discord)
   ↓
Nakama user (canonical identity)
   ↓
NetworkBridge links the incoming Minecraft UUID/name to that Nakama account
```

Pseudo-flow (server-side, in NetworkBridge):

```java
// OAuth token obtained from Discord/Google (not the offline MC UUID).
String oauthToken = getDiscordOrGoogleToken();   // verified by Nakama

NakamaSession session =
    nakama.authenticateGoogle(oauthToken, true, "google");

// Link the incoming offline Minecraft identity to this verified account.
String minecraftUuid = player.getUniqueId().toString();
nakama.linkCustom(session, minecraftUuid, player.getUsername());
```

Notes:

- `authenticateGoogle`/`authenticateApple` are built into Nakama. For Discord,
  register a **custom OAuth provider** (or use Nakama's custom auth once the
  token is validated) and call `authenticateCustom`.
- Store the Nakama session/token server-side, not on the vanilla Minecraft
  client.
- Never derive the canonical identity from an offline-mode UUID or username.

---

## 20.5 First test

Acceptance criteria:

```text
[ ] player joins Velocity
[ ] NetworkBridge can authenticate/find Nakama account
[ ] reconnect returns same Nakama identity
[ ] username changes do not create new social identity
[ ] a player cannot impersonate another player's identity by using their name
[ ] banned/verified OAuth account is rejected at the edge
```

Do not proceed to parties until this is deterministic.

---
