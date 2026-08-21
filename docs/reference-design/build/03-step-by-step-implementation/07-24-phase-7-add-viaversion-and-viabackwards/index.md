# Phase 7 — Add ViaVersion and ViaBackwards

At audit time:

```text
ViaVersion 5.11.0
ViaBackwards 5.11.0
```

Install on the proxy unless your compatibility test matrix requires a different placement.

Build an explicit compatibility matrix.

Example:

| Client | Backend runtime | Expected |
|---|---|---|
| current Java | current Paper | native |
| newer Java | older Paper | ViaVersion test |
| older supported Java | newer Paper | ViaBackwards test |
| vanilla client | Forge fantasy requiring mods | reject / launcher transition |

Do not say:

```text
ViaVersion installed -> every Minecraft version is now supported
```

Treat compatibility as tested contracts.

---
