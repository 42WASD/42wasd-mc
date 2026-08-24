# Add ViaVersion and ViaBackwards

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

# Add ViaVersion and ViaBackwards

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

## What the two plugins cover (direction of translation)

Both are *protocol* translators, not mod installers — so they only ever help
with the "vanilla wire protocol" direction, never with a client that lacks
required client-side mods.

- **ViaVersion** translates a *newer* client to an *older* server. Example:
  a 1.20 server accepting clients from ~1.9 up to the current release.
- **ViaBackwards** translates an *older* client to a *newer* server. It runs
  on servers 1.10–latest and accepts clients down to ~1.9.
- **ViaRewind** is needed only for 1.8–1.12 rewind (1.8 and older clients).

Exact supported ranges change with every Minecraft release — re-check
viaversion.com / the Hangar page at each bump, and keep the matrix above as
the tested contract rather than assuming "ViaVersion = everything works."

---
