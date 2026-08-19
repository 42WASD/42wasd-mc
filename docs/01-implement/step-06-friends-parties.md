# Step 6 — Friends + parties

Build the social graph on top of the stable Nakama identity from Step 5: friends lists, online/offline presence, and parties that players can form and join.

## Goal

Players can add friends, see each other's presence, and create/join a party — all keyed by the stable Nakama identity.

## Tasks

### 1. Friends

- Store friend edges (bidirectional) in Nakama, keyed by `nakama_user_id`.
- Provide add/remove/list operations.
- Presence is derived from where each identity is connected (which backend/server).

### 2. Parties

- Party has an owner (the member who created it).
- Invites carry an **invite policy** that decides who may join (friends-only, invitation, public).
- Party membership is resolved to **Nakama identities** (stable), not display names.

### 3. Presence

A player's presence is "on <server> on <backend>". Broadcast presence so friends see where everyone is (wire to TAB in Step 11).

## Acceptance criteria

```text
[ ] two friends can be added and listed
[ ] presence shows which backend each friend is on
[ ] a party can be created with an owner
[ ] party invites respect the configured invite policy
[ ] parties keyed by stable Nakama ID, not display name
```

## Note on invites

Invite policy (friends-only, public, etc.) is a **separate, well-defined concept** from map invites (Step 15). Both hang off the same identity.

## Next step

[Step 7 — Second static backend + /join](step-07-join.md)