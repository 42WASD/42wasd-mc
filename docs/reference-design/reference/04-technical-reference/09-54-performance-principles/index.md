# Performance principles

The proxy is not normally the expensive part.

The heavy components are:

```text
world generation
Forge modded simulation
MineColonies pathfinding
large mob/entity counts
chunk loading
disk saves
community maps with command/entity spam
```

Therefore prioritize:

```text
pre-generation where appropriate
entity limits
runtime-specific resource limits
spark profiling
PVC/NVMe placement for active worlds
sleep unused worlds
avoid too many always-loaded dimensions
```

Do not over-engineer proxy sharding before measuring it.

---
