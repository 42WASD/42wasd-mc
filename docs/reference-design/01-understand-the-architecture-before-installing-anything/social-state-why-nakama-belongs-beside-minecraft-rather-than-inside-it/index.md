# Social state: why Nakama belongs beside Minecraft rather than inside it

A proxy plugin can implement `/friend`, `/party`, and `/invite`.

The question is whether it should become the **authoritative database and realtime social system**.

Nakama already has the game-backend primitives:

```text
authentication identity
friends
parties
party invites
presence/status
notifications
chat
match/listing/matchmaking primitives
server runtime functions
```

Use Minecraft as one client/frontend of that social system.

---

## 7.1 Identity mapping

The canonical identity is the **Nakama user account, created via OAuth-first
social authentication** (Discord and/or Google). Minecraft identity is a linked,
secondary attribute — never the identity anchor.

Why OAuth-first: this network permits offline/cracked accounts behind the
authenticated proxy (see Phase 5). An offline-mode Minecraft UUID is generated
from the username and is spoofable — anyone can join with any name, so it
cannot be trusted as a canonical identity. A Discord/Google OAuth token proves
who the player is, prevents impersonation, and makes bans attach to a real,
verified account.

Example:

```text
Discord / Google OAuth token
       ↓
Nakama social-provider authentication (authenticateGoogle, or a custom OAuth
                                        provider for Discord)
       ↓
nakama_user_id  (canonical identity)
       ↓
linked Minecraft identity (per-lookup, see below)
```

Maintain a table/mapping such as:

```json
{
  "nakama_user_id": "....",
  "discord_id": "...",          // or google_id, if chosen
  "minecraft_uuid": "123e4567-e89b-12d3-a456-426614174000",
  "minecraft_name": "Steve"
}
```

The Minecraft UUID/name here are **runtime/presentation bindings** for the
current session, not the security anchor. They must be re-derived from the
verified Nakama session, never trusted from the offline client alone.

Do not make usernames authoritative; usernames can change.

### 7.1.1 Linking Minecraft UUID to the OAuth account

Because the backends run in offline mode, the proxy (Velocity NetworkBridge)
is the only party that sees both the OAuth-verified Nakama account and the
incoming Minecraft connection. It must bind them server-side:

```text
player joins Velocity
   ↓
NetworkBridge authenticates to Nakama with OAuth-verified session
   ↓
NetworkBridge links the incoming offline UUID/name to that Nakama account
      (Nakama account.link/custom, scoped to that session)
   ↓
backend sees the UUID the bridge assigned
```

The bridge, not the offline client, is the trusted source for the
UUID->Nakama mapping.

---

## 7.2 The Minecraft client does not need a Nakama SDK

The flow can remain fully server-side:

```text
Minecraft client
    ↓
Velocity NetworkBridge
    ↓
Nakama HTTP / realtime API
```

The proxy acts as a trusted broker.

That means ordinary vanilla clients do not install anything merely to use:

```text
/friend
/party
/invite
/join
/worlds
/random
```

---

## 7.3 Presence model

A useful status object:

```json
{
  "runtime_id": "backrooms-current",
  "map_id": "backrooms-level-0-a17",
  "backend_id": "map-a17",
  "dimension": "minecraft:overworld",
  "activity": "exploring",
  "joinable": true,
  "party_id": "optional"
}
```

This one object can power:

```text
TAB
/join <friend>
friend menu
invite routing
party-follow
web status page
```

---
