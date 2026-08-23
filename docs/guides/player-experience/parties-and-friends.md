# Parties & Friends

Configure the Nakama-powered social layer.

## Friends

- Friend edges are stored in Nakama, keyed by stable Nakama identity.
- Add / remove / list operations on the backend.
- Presence shows which server/backend each friend is on.

## Parties

- A party has an owner (who created it).
- Invites carry an **invite policy** (friends-only, invitation, public).
- Membership keys off stable Nakama IDs, not display names.

## Cross-runtime behavior

- Party membership and invites are **identity-based**.
- Runtime compatibility is checked separately, at join time — a fantasy map can
  host only fantasy-runtime clients.

## See also

- [Phase 15 — friends and parties](../../reference-design/03-step-by-step-implementation/implement-friends-and-parties/index.md)
- [Invite policy (reference)](../../reference-design/04-technical-reference/invite-policy/index.md)