# Nakama social state

Nakama sits **beside** Minecraft, not inside it. A proxy plugin could implement `/friend`, `/party`, `/invite` — but should it become the authoritative database and realtime social system? No.

Nakama already provides: authentication, friends, parties, party invites, presence/status, notifications, chat, matchmaking primitives, and server runtime functions.

## Identity mapping

The canonical identity is the authenticated Minecraft **UUID**:

```text
minecraft_uuid = 123e4567-e89b-12d3-a456-426614174000
     → Nakama custom authentication
     → nakama_user_id
```

Mapping:

```json
{
  "minecraft_uuid": "123e4567-e89b-12d3-a456-426614174000",
  "nakama_user_id": "....",
  "minecraft_name": "Steve"
}
```

Usernames can change; the UUID does not. Do not make usernames authoritative.

## The client does not need a Nakama SDK

```text
Minecraft client
  → Velocity NetworkBridge
  → Nakama HTTP / realtime API
```

The proxy is a trusted broker. Vanilla clients install nothing for `/friend`, `/party`, `/invite`, `/join`, `/worlds`, `/random`.

## Presence model

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

This one object powers TAB, `/join <friend>`, friend menus, invite routing, party-follow, and a web status page.