# Functional acceptance test

A release is not done until this passes:

## Network

```text
[ ] vanilla player joins public address
[ ] authenticated UUID preserved on Paper
[ ] backend cannot be joined publicly
[ ] correct account returns after launcher restart (join ticket)
[ ] offline UUID spoof cannot claim another user's Nakama identity
[ ] expired join ticket is rejected
[ ] consumed join ticket cannot be replayed
[ ] changing Minecraft username does not change account identity
[ ] logout invalidates launcher/session continuation
[ ] ViaVersion/ViaBackwards compatibility matrix passes per (client, backend)
    pair — a specific Via build can have cross-version regressions, so treat
    each combination as a tested contract, not a blanket "ViaVersion = OK"
```

## Via compatibility matrix

Keep an explicit tested matrix per Via release, e.g.:

| Client | Backend runtime | Expected | Status |
|---|---|---|---|
| current Java | current Paper | native | tested |
| newer Java | older Paper | ViaVersion | tested |
| older supported Java | newer Paper | ViaBackwards | tested |
| vanilla client | Forge fantasy requiring mods | reject / launcher transition | tested |

Re-verify on every Via bump (a specific release can have a cross-version
regression). Protocol connectivity ≠ mod compatibility.

## Social

```text
[ ] friend add/accept works
[ ] presence shows backend/map
[ ] party persists across backend transfer
```

## Dynamic world

```text
[ ] sleeping world replicas=0
[ ] /join wakes world
[ ] player stays in lobby while starting
[ ] player transfers only after Minecraft readiness
[ ] world sleeps after configured idle time
[ ] PVC survives stop/start
[ ] GameServerSet 1 -> 0 preserves PVC
[ ] 0 -> 1 mounts the same world
[ ] World Controller is the sole replica writer for named worlds
[ ] Argo CD does not reset dynamic replicas/status
[ ] KEDA is not attached to a World-Controller-owned GameServerSet
```

## Random portal

```text
[ ] only runtime-compatible maps are candidates
[ ] capacity is reserved
[ ] party moves together
[ ] failed startup returns users to safe lobby
```

## Modded runtime

```text
[ ] correct fantasy pack connects
[ ] compatible fantasy backend switching works
[ ] wrong vanilla client receives controlled runtime requirement
[ ] Modrinth install/update path works
[ ] reconnect consumes pending invite
[ ] correct account returns after restart
[ ] pending invite survives restart
```

## Launcher (Server Project integration)

```text
[ ] official Modrinth Server Project flow works
[ ] AstralRinth can consume the required runtime
[ ] server-project update reaches the linked runtime
```

## TAB

```text
[ ] global users visible
[ ] server/map information updates
[ ] exact dimension updates after world change
```

---
