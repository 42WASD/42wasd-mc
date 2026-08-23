# Add exact world/dimension TAB information

Backend bridge sends world change:

```json
{
  "player_uuid": "...",
  "runtime_id": "vanilla-current",
  "map_id": "survival-main",
  "dimension": "minecraft:the_nether"
}
```

Store/update presence.

NetworkBridge exposes:

```text
<network_map>
<network_runtime>
<network_dimension>
```

TAB then displays:

```text
Fantasy Kingdom
  Ahmad — Overworld
  Alex  — The Nether

Backrooms
  Steve — Level 0
```

Do not infer dimension from proxy server name.

---
