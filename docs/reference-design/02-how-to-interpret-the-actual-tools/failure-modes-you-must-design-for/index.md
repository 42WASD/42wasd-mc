# Failure modes you must design for

## World is “Running” but Minecraft is not ready

Bad:

```text
Pod phase = Running
-> transfer player
```

Better:

```text
Pod Ready
AND
Minecraft status/ping successful
AND
backend registered
-> transfer
```

---

## Two players wake the same world simultaneously

Use an idempotent transition:

```text
ensureWorldReady(map_id)
```

not:

```text
startWorld(map_id)
```

The call must safely converge if ten requests arrive simultaneously.

---

## Party is split during transfer

Reserve capacity for the full party.

Do not independently random-route members.

---

## Invite target changed during launcher restart

Pending invite should contain:

```text
inviter
target runtime_id
target map_id
creation time
expiry
mode
```

On reconnect:

```text
if inviter moved and mode=FOLLOW_INVITER:
    resolve new location
else:
    use original target map
```

Make this explicit.

---

## Modded map updates while players have old runtime

Never mutate a runtime contract without versioning it.

Bad:

```text
fantasy-runtime -> silently replace 15 required mods
```

Better:

```text
fantasy-1.20.1-r3
fantasy-1.20.1-r4
```

Drain r3 and migrate intentionally.

---

## Community map contains malicious or broken content

Treat uploaded worlds as untrusted.

Perform:

```text
size limits
archive validation
path traversal protection
malware scan
allowed file-type checks
no arbitrary startup scripts
runtime-class allowlist
server-side plugin/mod allowlist
manual approval for executable additions
```

---

## Sleeping world never wakes

Timeout and fall back (a world stuck in `STARTING` past its timeout is marked
`DEGRADED` — an operational flag outside the normal `ASLEEP`/`STARTING`/`READY`/
`STOPPING` state axis, never served to players):

```text
start
  ↓ timeout
mark DEGRADED
  ↓
return player to lobby
  ↓
surface operator alert
```

Never leave the player in an infinite “Connecting…” loop.

---

## Backend becomes publicly reachable

This is a serious authentication/security failure because backend servers are normally in offline mode behind the proxy.

Use:

```text
public exposure: proxy only
backend Services: ClusterIP
network policy/firewall
Velocity modern forwarding secret
```

Do not rely on forwarding secrets as the only firewall.

---
