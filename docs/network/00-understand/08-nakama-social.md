# Social state: why Nakama belongs beside Minecraft rather than inside it

A proxy plugin can implement `/friend`, `/party`, and `/invite`. The question is whether it should become the **authoritative database and realtime social system**.

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

## Identity mapping

The canonical identity should be the authenticated Minecraft UUID:

```text
minecraft_uuid = 123e4567-e89b-12d3-a456-426614174000
       ↓
Nakama custom authentication ID
       ↓
nakama_user_id
```

Maintain a mapping table:

```json
{
  "minecraft_uuid": "123e4567-e89b-12d3-a456-426614174000",
  "nakama_user_id": "....",
  "minecraft_name": "Steve"
}
```

Do **not** make usernames authoritative; usernames can change.

## The Minecraft client does not need a Nakama SDK

The flow can remain fully server-side:

```text
Minecraft client → Velocity NetworkBridge → Nakama HTTP / realtime API
```

The proxy acts as a trusted broker. That means ordinary vanilla clients do not install anything merely to use:

```text
/friend /party /invite /join /worlds /random
```

## Presence model

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

This one object can power TAB, `/join <friend>`, friend menus, invite routing, party-follow, and a web status page.