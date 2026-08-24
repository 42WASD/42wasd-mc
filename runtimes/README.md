# runtimes/

Reusable Minecraft server runtimes (software stacks + versions), indexed by
runtime slug. A runtime is the *software* a world runs on; a map is the
*world data* a runtime loads.

```text
runtimes/
├── vanilla-current/      # plain current-version Minecraft
├── backrooms-current/    # Backrooms content pack
└── fantasy-1.20.1-forge/ # fantasy modpack (Forge 1.20.1)
```

Each runtime directory documents its image, version pin, and any mods/plugins.
Runtimes are referenced by worlds (see `maps/`) via runtime-id.