# Runtime classes

A runtime class is a **compatibility contract**: the Minecraft version, loader, required client mods, and server capabilities a map may assume. Define a small number of them.

## Runtime A — `vanilla-current`

```yaml
id: vanilla-current
kind: paper
minecraft_protocol_policy: via-compatible
client_modpack_required: false
server_resource_pack: optional
community_maps_allowed: true
```

**For:** lobby, ordinary survival, community adventure maps, minigames, creative/build, lightweight horror. Most seamless experience.

## Runtime B — `backrooms-current`

```yaml
id: backrooms-current
kind: paper
client_modpack_required: false
required_resource_pack: true
community_maps_allowed: true
```

Prefer server-side implementation (resource packs, plugins, datapacks, custom model data, display entities, server mechanics). **Why:** `invite → click Join → transfer immediately` beats restarting Minecraft for every horror map.

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

**Possible content:** MineColonies, Ice and Fire, Cataclysm, fantasy mobs, structure/worldgen mods, performance mods. Every map in this class uses the **same client registry/modpack contract**. A map author may contribute worlds, schematics, quests, scripts, allowed server configs, resource packs, and metadata — but cannot silently add an arbitrary client-required mod.

## Runtime D — `experimental-*`

Separate, opt-in experiences:

```text
experimental-horror-1
experimental-tech-1
experimental-rpg-2
```

Each can have its own Modrinth Server Project and may require a launcher restart. **Never** put them in the random instant-portal pool for clients not already running that runtime.

## The rule

> **A community map may be dynamic; the required client runtime must be standardized.**