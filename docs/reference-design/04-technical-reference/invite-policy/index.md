# Invite policy

## Invite modes

Possible invite modes:

```text
JOIN_MAP        join a specific world/map
FOLLOW_INVITER  follow the inviter to wherever they are
JOIN_PARTY      join the inviter's party
JOIN_SESSION    join a transient session (Agones match)
```

Recommended default for friend invites:

```text
FOLLOW_INVITER until accepted
then freeze target during transfer
```

This prevents chasing a friend across servers while startup is in progress.

## Invite record (schema)

The invite object lives in **Nakama** (it owns invites/presence). It records
*user intent*, not authentication — it is keyed by the canonical **Nakama user
ID**, never the spoofable offline Minecraft UUID. One record per invite; it
survives launcher restarts so a reconnect can consume it (see
[implement-pending-cross-runtime-invites](../../03-step-by-step-implementation/implement-pending-cross-runtime-invites/index.md)).

```json
{
  "id": "invite-uuid",
  "mode": "FOLLOW_INVITER",
  "inviter_user_id": "<nakama-user-id>",
  "recipient_user_id": "<nakama-user-id>",
  "target_runtime_id": null,   // null until acceptance for FOLLOW_INVITER; set for JOIN_MAP
  "target_map_id": null,       // null until acceptance for FOLLOW_INVITER; set for JOIN_MAP
  "state": "PENDING",
  "created_at": "2026-08-19T...",
  "expires_at": "2026-08-19T..."
}
```

> `target_runtime_id`/`target_map_id` are **nullable**: for `FOLLOW_INVITER`
> they are `null` until acceptance, when the World Controller resolves the
> inviter's current runtime/map. For `JOIN_MAP` they are populated at invite
> creation. The schema below marks them nullable to match that behavior.

### Invite state machine

```text
PENDING  ── accepted ──► ACCEPTED ── routed ──► CONSUMED
    │
    ├── declined ──────────► DECLINED
    ├── expired ───────────► EXPIRED
    ├── invalid (runtime) ─► EXPIRED
    └── launcher restart ───► PENDING (kept, not consumed)
```

- An invite stays `PENDING` across a launcher restart; on reconnect the
  NetworkBridge re-resolves it (see the pending-invite flow).
- `ACCEPTED` → the World Controller begins `ensure-ready` + transfer, then the
  record flips to `CONSUMED` (or `EXPIRED` if the target is no longer valid).
- `target_runtime_id`/`target_map_id` may be empty/`null` for `FOLLOW_INVITER`
  until acceptance — the World Controller resolves the inviter's current
  runtime/map at that moment.

### Join ticket (authentication, distinct from the invite)

The **invite is user intent; it is not a credential.** Who actually came back
after a launcher restart is proven by a **join ticket**, not by the invite
record. The Auth / Join-Ticket Service mints it (scoped to the authenticated
Nakama session the launcher holds) and Velocity validates + consumes it once:

```json
{
  "jti": "ticket-uuid",
  "sub": "<nakama-user-id>",
  "aud": "velocity",
  "runtime_id": "fantasy-1.20.1-r4",
  "invite_id": "invite-uuid",   // the intent to resolve after auth
  "exp": "2026-08-19T...",
  "single_use": true
}
```

- The invite survives the launcher restart (user intent).
- The join ticket proves who came back (authentication proof).
- They are not the same thing: the ticket may reference an invite, but the
  ticket's validity is tied to the authenticated Nakama session, not to the
  invite record.

### Matching modes to routing

| Mode            | Resolves target when | Behavior on acceptance |
|-----------------|----------------------|------------------------|
| `JOIN_MAP`      | at invite creation   | ensure-ready for that map |
| `FOLLOW_INVITER`| at acceptance        | route to inviter's current runtime/map (freeze target) |
| `JOIN_PARTY`    | at acceptance        | route into the party's world |
| `JOIN_SESSION`  | at acceptance        | atomic session allocation (Agones, optional) |

---
