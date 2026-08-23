# Joining & Invites

How players join the network and how invites work — including cross-runtime
invites.

## Joining

- A player connects to the public host, authenticates through the proxy, and
  lands in the lobby.
- `/join <server>` moves a player to a named backend.
- `/join <friend>` joins a friend's backend (see
  [Phase 14](../../reference-design/03-step-by-step-implementation/implement-join-friend/index.md)).

## Invites

- An invite carries a **target map** and thus a **runtime**.
- **Invite policy** decides *who may join* (friends-only, etc.).
- **Runtime compatibility** decides whether a given player *can* join.
- A vanilla player invited to a Forge map is blocked unless they install the
  required runtime (see
  [Phase 15 — cross-runtime invites](../../reference-design/03-step-by-step-implementation/implement-pending-cross-runtime-invites/index.md)).

## See also

- [Invite policy (reference)](../../reference-design/04-technical-reference/invite-policy/index.md)
- [Parties & Friends](parties-and-friends.md)