# Implement pending cross-runtime invites

## Two distinct objects

The **invite** (user intent) and the **join ticket** (authentication proof) are
separate. The invite survives a launcher restart; the join ticket proves who
came back on each connection. See
[invite-policy](../../04-technical-reference/invite-policy/index.md).

Invite record (in Nakama, keyed by Nakama user IDs — never the offline UUID):

```json
{
  "id": "invite-uuid",
  "inviter_user_id": "<nakama-user-id>",
  "recipient_user_id": "<nakama-user-id>",
  "target_runtime_id": "fantasy-1.20.1-r4",
  "target_map_id": "fantasy-kingdom-001",
  "mode": "FOLLOW_INVITER",
  "state": "PENDING",           // PENDING -> ACCEPTED -> CONSUMED/DECLINED/EXPIRED
  "created_at": "2026-08-19T...",
  "expires_at": "2026-08-19T..."
}
```

## End-to-end flow

```text
invite created (recipient has an incompatible runtime)
   ↓
recipient accepts
   ↓
runtime incompatibility detected
   ↓
intent stored as PENDING (survives restart)
   ↓
launcher installs/updates the required runtime (Modrinth Server Project)
   ↓
launcher mints a one-time JOIN TICKET from its authenticated Nakama session
   ↓
launch Minecraft against the ticket hostname (see "Join-ticket transport"
   in social-state 7.1.2)
   ↓
Velocity / NetworkBridge validates + CONSUMES the ticket
   ↓
pending intent recovered (the invite)
   ↓
World Controller ensure-ready (wake)
   ↓
transfer
   ↓
consume pending invite
```

This makes the restart feel like one continuous invite flow — and the join
ticket, not the invite, is what authenticates the reconnect.

---
