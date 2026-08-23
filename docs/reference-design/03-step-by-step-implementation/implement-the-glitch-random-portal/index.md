# Implement the glitch/random portal

Backend trigger:

```text
player touches portal region
```

Request:

```http
POST /v1/routes/random
```

Body:

```json
{
  "player_uuid": "...",
  "party_id": null,
  "runtime_id": "backrooms-current",
  "tags": ["backrooms"],
  "exclude_recent": true
}
```

Selection pipeline:

```text
all maps
    ↓
enabled?
    ↓
runtime compatible?
    ↓
random eligible?
    ↓
capacity?
    ↓
party policy?
    ↓
not recently visited?
    ↓
weighted random
```

Then:

```text
reserve
ensure-ready
play glitch audiovisual effect
transfer
```

---

## Never randomly select an incompatible client runtime

Bad:

```text
vanilla player
-> random
-> Forge-only map
-> disconnect with missing mods
```

Good:

```text
random pool is filtered by current runtime
```

If you want a cross-runtime “mystery invite,” make it an explicit launcher transition experience.

---
