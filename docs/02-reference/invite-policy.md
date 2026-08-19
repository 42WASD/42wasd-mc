# Invite policy

Invites govern **who may join** a party (Step 6) or a map (Step 15). Invite policy is evaluated **separately** from runtime compatibility.

## Invite policy levels

| Policy | Meaning |
|--------|---------|
| `public` | anyone may join |
| `friends-only` | only friends (Step 6) may accept |
| `invite-only` | only explicitly invited players may join |

## Invite carry

A map invite carries the target **map** and thus its **runtime**:

```text
Invite { targetMapId, runtimeId, policy, invitedPlayers: [nakamaId], expiresAt }
```

## Runtime vs policy

- **Policy** decides *who may join* (social).
- **Runtime** decides *whether a given player can physically play* (Step 12/13).

A `friends-only` invite to a `fantasy-1.20.1-forge` map:
- The vanilla friend **may** be invited (policy passes).
- But will be **blocked** on join unless their client runtime matches (or they install the fantasy runtime, Step 14).

## See also

- [Step 6 — Friends + parties](../01-implement/step-06-friends-parties.md)
- [Step 15 — Cross-runtime invite](../01-implement/step-15-cross-runtime-invite.md)
- [Step 14 — Modrinth Server Project](../01-implement/step-14-modrinth.md)