# Functional acceptance test

A release is not done until this passes.

## Network

```text
[ ] vanilla player joins public address
[ ] authenticated UUID preserved on Paper
[ ] backend cannot be joined publicly
```

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
```

## TAB

```text
[ ] global users visible
[ ] server/map information updates
[ ] exact dimension updates after world change
```