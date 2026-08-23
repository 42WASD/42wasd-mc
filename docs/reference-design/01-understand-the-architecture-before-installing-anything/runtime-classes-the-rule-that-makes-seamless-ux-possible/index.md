# Runtime classes: the rule that makes seamless UX possible

Define a small number of supported runtime contracts.

> **Field shapes below are a simplified, reader-friendly summary.** The
> canonical `RuntimeDefinition` schema uses a nested, flat-top-level snake_case
> shape and is the single source of truth for `runtimes/<id>/runtime.yaml`. See
> [runtimedefinition-schema](../../04-technical-reference/runtimedefinition-schema/index.md).
> The examples here flatten a few of its nested fields (e.g. `kind` ↔
> `minecraft.server_type`) for quick reading.

## Runtime A — `vanilla-current`

Example:

```yaml
id: vanilla-current
kind: paper
minecraft_protocol_policy: via-compatible
client_modpack_required: false
server_resource_pack: optional
community_maps_allowed: true
```

Use for:

- lobby;
- ordinary survival;
- community adventure maps;
- minigames;
- creative/build worlds;
- lightweight horror experiences.

This runtime should provide the most seamless experience.

---

## Runtime B — `backrooms-current`

Prefer a Paper/server-side implementation where possible:

```yaml
id: backrooms-current
kind: paper
minecraft_protocol_policy: via-compatible
client_modpack_required: false
required_resource_pack: true
community_maps_allowed: true
```

Use resource packs, server-side plugins, datapacks, custom model data, sounds, display entities, and server mechanics where possible.

Why?

Because:

```text
invite
  ↓
click Join
  ↓
transfer immediately
```

is a much better user experience than restarting Minecraft for every horror map.

---

## Runtime C — `fantasy-1.20.1-forge`

Example contract:

```yaml
id: fantasy-1.20.1-forge
kind: forge
minecraft_version: "1.20.1"
client_modpack_required: true
modpack_id: "fantasy-runtime"
proxy_compatibility: "velocity + ambassador + ProxyCompatibleForge"
community_maps_allowed: true
```

Possible content:

```text
MineColonies
Ice and Fire
Cataclysm
fantasy mobs
structure/worldgen mods
performance mods
```

Every map in this class uses the **same required client registry/modpack contract**.

A map author may contribute:

```text
world data
schematics
quests
scripts
server configs allowed by policy
resource packs
map metadata
```

but cannot silently add an arbitrary client-required mod.

---

## Runtime D — `experimental-*`

These are intentionally separate experiences:

```text
experimental-horror-1
experimental-tech-1
experimental-rpg-2
```

Each can have its own Modrinth Server Project.

They are allowed to require launcher restart.

Do not put them into the random instant-portal pool for clients that are not already running that runtime.

---
