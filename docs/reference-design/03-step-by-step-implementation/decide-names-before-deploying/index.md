# Decide names before deploying

Use stable identifiers. Do not use user-facing display names as primary keys.

## Cluster / environment

| Layer | Name | Notes |
|-------|------|-------|
| Cluster (kube context) | `alpha-games-prd` | Production games cluster (`alpha`) |
| Production namespace | `prd-games-42wasd-admin` | All game workloads live here |
| Dev namespace | `dev-games-42wasd-admin` | Ephemeral mirror of prd for debugging / upgrade dry-runs; created one-to-one, then deleted |
| Public host | `minecraft.42base.com` | Registered on Cloudflare; points at Velocity |

The reference design's generic `minecraft` / `minecraft-system` namespaces are
**adapted** to the tenant-namespace policy that actually exists on the cluster
(`prd-games-42wasd-admin` / `dev-games-42wasd-admin`). Per the design: *"If you
already have tenant-specific namespace policy, adapt this rather than bypassing
it."*

## Logical ID scheme

World logical IDs use a **non-collision text convention**: a human-readable
slug plus an 8-hex-character prefix of the world's canonical UUID.

```text
<map-slug>-<uuid8>
```

- `<map-slug>` — lowercase, dash-separated, human-readable map name.
- `<uuid8>` — the first 8 hex characters of the map's canonical UUID
  (UUID v4). ~4.3&nbsp;billion combinations; effectively collision-free.
- The full 32-char UUID is recorded as metadata on the object
  (`uuid.42wasd.dev/map` label/annotation), not in the object name.
- Names must be **DNS subdomain / RFC-1123-label valid**: ≤ 63 chars,
  lowercase alphanumeric + `-`, start/end with an alphanumeric, start with an
  alphabetic character.

## ID vocabulary

```text
Runtime ID:  <runtime-slug>-<pack-revision>
MapDef:      <map-slug>
MapInstance: <map-slug>-<uuid8>

Lobby:       lobby-1          (always-on, not a map — fixed service)
```

## Recorded identifiers

```text
Kubernetes namespace (prd): prd-games-42wasd-admin
Kubernetes namespace (dev): dev-games-42wasd-admin
Public host:                minecraft.42base.com

Runtime IDs:
  vanilla-current-r0
  fantasy-1.20.1-forge-r4

Backend logical IDs (map instance):
  survival-main-3f9a2c1b
  backrooms-7e1d4b90
  fantasy-kingdom-a5c09f31

Fixed backends:
  lobby-1
```

## Rules

- Map instances are **derived**, not stored: given a map's fixed UUID,
  `uuid8 = uuid[:8]`, so re-creating a map always yields the same object name
  and GitOps reconciliation stays deterministic.
- Never reuse the ordinal `-001` style: it collides across delete/recreate.
- User-facing display names are presentation metadata only (a label), never
  the primary key.

---
