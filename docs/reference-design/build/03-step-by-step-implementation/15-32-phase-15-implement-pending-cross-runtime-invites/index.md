# Phase 15 — Implement pending cross-runtime invites

Data contract:

```json
{
  "id": "invite-uuid",
  "recipient_minecraft_uuid": "...",
  "inviter_minecraft_uuid": "...",
  "target_runtime_id": "fantasy-1.20.1-forge",
  "target_map_id": "fantasy-kingdom-001",
  "mode": "FOLLOW_INVITER",
  "created_at": "2026-08-19T...",
  "expires_at": "2026-08-19T..."
}
```

When the player reconnects:

```text
player authenticated
    ↓
NetworkBridge queries pending joins
    ↓
validate current client/runtime compatibility
    ↓
resolve target
    ↓
ensure-ready
    ↓
transfer
    ↓
consume pending join
```

This is what makes the restart feel like one continuous invite flow.

---
