# Maturity and deployment tiers

## Tier A — foundation

Use immediately:

```text
Velocity
TAB
ViaVersion + ViaBackwards
itzg/minecraft-server
OpenKruiseGame GameServerSet + PVC
World Controller
```

These form the minimum dynamic network.

---

## Tier B — product/social layer

Add next:

```text
Nakama
CockroachDB
NetworkBridge
friends
parties
invites
presence
world browser
```

---

## Tier C — operational efficiency

Add after basic switching works:

```text
mc-router
scale-to-zero
idle draining
Prometheus metrics
backups
```

---

## Tier D — client-runtime UX

Add once modded fantasy is stable:

```text
Modrinth Server Project
packwiz CI
pending cross-runtime invite
```

---

## Tier E — session matchmaking

Add only when needed:

```text
Agones
warm fleets
atomic GameServerAllocation
FleetAutoscaler
```

---
