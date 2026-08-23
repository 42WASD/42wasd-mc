# End-to-end user experiences

## Example A — Join a vanilla friend instantly

```text
Steve is in lobby.
Alex is in vanilla survival.
Steve types /join Alex.

NetworkBridge
    ↓ resolves Alex presence in Nakama
World Controller
    ↓ confirms world is ready
Velocity
    ↓ transfers Steve
Backend
    ↓ spawns Steve according to join policy
```

No restart.

---

## Example B — Friend is in a sleeping community map

```text
Alex invites Steve
    ↓
Nakama records invite
    ↓
Steve accepts
    ↓
World Controller sees replicas=0
    ↓
scale GameServerSet 0 -> 1
    ↓
wait for K8s Ready
    ↓
wait for Minecraft protocol readiness
    ↓
register backend
    ↓
Velocity transfers Steve
```

The player may remain in lobby with:

```text
"Starting Floating Kingdom…"
```

Do not transfer to a TCP port merely because the Pod exists.

---

## Example C — “Glitch me somewhere”

```text
Player enters unstable portal
    ↓
backend sends route request
    ↓
World Controller filters map catalog:
      runtime compatible?
      map enabled?
      enough capacity?
      party allowed?
      recently visited?
    ↓
weighted random selection
    ↓
wake / allocate
    ↓
play glitch transition
    ↓
transfer
```

For a party, reserve capacity for the entire party before routing the leader.

---

## Example D — Invite crosses into the fantasy Forge runtime

Steve is currently running the vanilla runtime.

Alex is in:

```text
fantasy-1.20.1-forge
```

Flow:

```text
Alex -> /invite Steve
        ↓
Nakama stores pending invite:
  target_runtime=fantasy-1.20.1-forge
  target_map=kingdom-7
  inviter=Alex
  expires_at=...
        ↓
Steve sees:
"This world requires Fantasy Runtime."
[Install / Launch Runtime]
        ↓
Modrinth Server Project
        ↓
installs/updates required content
        ↓
launches the correct Minecraft runtime into your public server
        ↓
NetworkBridge authenticates Steve
        ↓
looks up pending invite
        ↓
World Controller starts/resolves kingdom-7
        ↓
Velocity transfers Steve
```

The launcher restart is real, but the user does **not** need to manually discover mods, loader versions, or server addresses.

---
