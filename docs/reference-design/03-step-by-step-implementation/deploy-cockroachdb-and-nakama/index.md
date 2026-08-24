# Deploy CockroachDB and Nakama

## Why CockroachDB

Nakama is built around **PostgreSQL-wire-compatible** database semantics, and
PostgreSQL examples do exist in official Nakama material. That said, current
formal Nakama installation documentation continues to identify **CockroachDB
as the officially supported and optimized production target**, and describes
PostgreSQL support as unofficial/development-focused.

**42WASD standardizes production Nakama on CockroachDB** for its distributed,
auto-healing behavior on Kubernetes. Do **not** claim "PostgreSQL is
unsupported" (it works in dev) and do **not** claim "PostgreSQL is fully
equivalent" (it is not the production-optimized target).

---

## Deploy CockroachDB

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

## Deploy Nakama 3.40.0

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

## Create identity authentication (OAuth-first)

The canonical identity is the **Nakama account created via Discord/Google OAuth**
(see [Social state: why Nakama belongs beside Minecraft rather than inside it](../../01-understand-the-architecture-before-installing-anything/social-state-why-nakama-belongs-beside-minecraft-rather-than-inside-it/index.md)).
This is what prevents abuse from anonymous users and removes the
need to build your own user management. The offline Minecraft UUID is only a
runtime binding, never the identity anchor.

Flow when a player first connects through Velocity (in-game auth gate):

```text
player joins network -> lands on the gate/login stage (not a world)
   ↓
Discord/Google OAuth completed at the gate (browser or in-game prompt)
   ↓
Nakama social-provider authentication (authenticateGoogle for Google;
  for Discord our auth layer / runtime hook validates the token and maps the
  verified user ID into Nakama Custom Authentication)
   ↓
Nakama user (canonical identity)
   ↓
NetworkBridge links the incoming Minecraft UUID/name to that Nakama account
   ↓
gate routes the now-authenticated player to the lobby/world
```

Pseudo-flow (server-side, in NetworkBridge / Auth Service):

```java
// OAuth token obtained from Discord/Google (not the offline MC UUID).
String oauthToken = getDiscordOrGoogleToken();   // verified by Nakama

NakamaSession session =
    nakama.authenticateGoogle(oauthToken, true, "google");
```

Notes:

- `authenticateGoogle` is built into Nakama. **Discord is not built-in**: our
  auth layer / Nakama `beforeAuthenticateCustom` hook validates the Discord
  token and maps its verified user ID into Nakama Custom Authentication
  (`authenticateCustom`).
- Store the Nakama session/token in the **launcher's private storage**, not on
  the vanilla Minecraft client.
- Never derive the canonical identity from an offline-mode UUID or username.
- **Do not link the raw offline Minecraft UUID as a Nakama authentication
  identity.** Offline UUIDs can be spoofed, so they must never be a way to
  select a credential-bearing Nakama account. The verified external identity
  (Discord/Google/Microsoft) is the only authentication mechanism; the
  Minecraft UUID/name is **profile/presence metadata** mapped onto the Nakama
  user, not an auth identity:

  ```text
  Google/Discord/Microsoft OAuth
        ↓ (verify)
  Nakama User ID  ← the authentication identity
        ├── friends / parties / invites / account
        └── Minecraft identity mapping
              current_name
              observed_uuid
              launcher_account
  ```

---

## First test

Acceptance criteria:

```text
[ ] player joins Velocity
[ ] NetworkBridge can authenticate/find Nakama account
[ ] reconnect returns same Nakama identity
[ ] username changes do not create new social identity
[ ] a player cannot impersonate another player's identity by using their name
[ ] banned/verified OAuth account is rejected at the edge
```

The NetworkBridge-facing criteria are validated **retroactively** once the
NetworkBridge is built (a later phase). The parts that depend on NetworkBridge
glue should be re-checked at that point; the DB and Nakama deploy themselves
are complete once Nakama serves the OAuth identity API and the first test
account persists.

Do not proceed to parties until this is deterministic.

---
