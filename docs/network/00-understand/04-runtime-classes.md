# Runtime classes: the rule that makes seamless UX possible

Define a small number of supported runtime contracts. This is the key product decision.

## Runtime A — `vanilla-current`

```yaml
id: vanilla-current
kind: paper
minecraft_protocol_policy: via-compatible
client_modpack_required: false
server_resource_pack: optional
community_maps_allowed: true
```

**Use for:** lobby, ordinary survival, community adventure maps, minigames, creative/build worlds, lightweight horror experiences.

This runtime should provide the most seamless experience.

## Runtime B — `backrooms-current`

Prefer a Paper/server-side implementation where possible:

```yaml
id: backrooms-current
kind: paper
client_modpack_required: false
required_resource_pack: true
community_maps_allowed: true
```

Use resource packs, server-side plugins, datapacks, custom model data, sounds, display entities, and server mechanics where possible.

**Why?** Because:

```text
invite → click Join → transfer immediately
```

is a much better user experience than restarting Minecraft for every horror map.

## Runtime C — `fantasy-1.20.1-forge`

```yaml
id: fantasy-1.20.1-forge
kind: forge
minecraft_version: "1.20.1"
client_modpack_required: true
modpack_id: "fantasy-runtime"
proxy_compatibility: "velocity + ambassador + proxycompatibleforge"
community_maps_allowed: true
```

**Possible content:** MineColonies, Ice and Fire, Cataclysm, fantasy mobs, structure/worldgen mods, performance mods.

Every map in this class uses the **same required client registry/modpack contract**. A map author may contribute world data, schematics, quests, scripts, allowed server configs, resource packs, and map metadata — but cannot silently add an arbitrary client-required mod.

## Runtime D — `experimental-*`

Intentionally separate experiences:

```text
experimental-horror-1
experimental-tech-1
experimental-rpg-2
```

Each can have its own Modrinth Server Project. They are allowed to require launcher restart. Do **not** put them into the random instant-portal pool for clients that are not already running that runtime.