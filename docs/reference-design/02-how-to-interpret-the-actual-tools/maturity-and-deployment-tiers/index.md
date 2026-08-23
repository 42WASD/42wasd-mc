# Maturity and deployment tiers

## Tier A — foundation

Use immediately:

```text
Velocity
TAB
ViaVersion + ViaBackwards
itzg/minecraft-server
itzg/mc-monitor (readiness + metrics)
OpenKruiseGame GameServerSet + PVC
World Controller
```

These form the minimum dynamic network.

> **Security gate (important):** the backends in Tier A run in offline mode and
> are only safe because they sit behind the authenticated proxy. Do **not**
> expose them publicly until the Nakama-gated Velocity exists (Tier B +
> `deploy-velocity`/`build-networkbridge-for-velocity`). In the build order this
> means CockroachDB + Nakama (Phase 5) are deployed **before** Velocity (Phase 6)
> and the Paper lobby (Phase 7), so the gate is in place before any backend is
> reachable.

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

> Tier B is a hard prerequisite for exposing the Tier A backends, not an
> optional add-on — see the note above.

---

## Tier C — operational efficiency

Add after basic switching works:

```text
mc-router
KEDA (scale-to-zero trigger)
scale-to-zero
idle draining
Prometheus metrics (scraping mc-monitor output, KEDA triggers)
Velero (PVC backups)
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
