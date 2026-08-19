# End-to-end user experiences

## A. Join a vanilla friend instantly

```text
Steve types /join Alex
  → NetworkBridge resolves Alex's presence in Nakama
  → World Controller confirms world ready
  → Velocity transfers Steve
  → Backend spawns Steve
```

No restart.

## B. Friend is in a sleeping community map

```text
Alex invites Steve → Nakama records invite → Steve accepts
  → World Controller sees replicas=0
  → scale StatefulSet 0→1
  → wait K8s Ready → wait Minecraft Ready → register backend
  → Velocity transfers Steve
```

Player stays in the lobby ("Starting Floating Kingdom…"). Do **not** transfer merely because the Pod exists.

## C. "Glitch me somewhere"

```text
Player enters unstable portal
  → backend sends route request
  → World Controller filters catalog (runtime, enabled, capacity, party, recent)
  → weighted random selection
  → wake/allocate → play glitch transition → transfer
```

For a party, reserve capacity for the whole party before routing the leader.

## D. Invite crosses into the fantasy Forge runtime

Steve runs vanilla; Alex is in `fantasy-1.20.1-forge`.

```text
Alex → /invite Steve
  → Nakama stores pending invite (target_runtime, target_map, inviter, expiry)
  → Steve sees "This world requires Fantasy Runtime." [Install / Launch]
  → Modrinth Server Project installs/updates and launches the runtime
  → NetworkBridge authenticates Steve → resolves the pending invite
  → World Controller starts the map → Velocity transfers Steve
```

The launcher restart is real, but Steve never manually discovers mods, loader versions, or server addresses.