# maps/

World data and map definitions. A map is the *world content* a runtime loads;
each map carries a logical ID per the Phase 0 naming convention:

`<map-slug>-<uuid8>` where `<uuid8>` is the first 8 hex chars of the map's
canonical UUID. The full UUID is stored on the `uuid.42wasd.dev/map` label.

```text
maps/
├── survival-main/       # survival-main-<uuid8> (logical ID)
└── backrooms-level-0/   # backrooms-level-0-<uuid8>
```

World data is not checked into git — see the `world-data/` export directory
(ignored). These directories hold the *definitions and metadata* for each map.