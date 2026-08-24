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

# Minecraft server performance (MSPT headroom & player scale)

**Intent:** capture the approach to keep a Paper/modded server at 20 TPS with
MSPT headroom for many players, **without** presenting workload-dependent
tuning folklore as universal facts. The platform repo only sets generic policy;
this page is the game-layer reference, kept as a *method* (measure → tune →
accept) rather than a fixed set of "rules".

## 1. Performance contract

- Target **20 TPS** — the game clock is fixed at 20 ticks/second (one tick
  every 50 ms). Staying at 20 TPS means **MSPT stays under 50 ms**.
- Define a headroom target (e.g. MSPT max ≤ ~30–40 ms at peak) and a
  **p95/p99 MSPT** goal per runtime so regressions are measurable.
- **Ping ≠ TPS.** Player ping is network RTT; TPS is server processing speed.
  A 20-TPS server can still show high ping for a distant player. Optimizing
  MSPT does not lower ping.

### Reading the numbers
- `tps` → 20.0 / 20.0 / 20.0 is perfect.
- `mspt` (Paper) → watch the **max** (spikes), not only avg.
- `spark healthreport` → automated tick/CPU/disk/GC health check.

## 2. Measure before tuning

Never tune from lore; profile the actual workload first:

```text
spark profiler / healthreport
backend Prometheus metrics (TPS/MSPT if exported)
CPU throttling (cgroup/limits)
GC (spark or GC logs)
disk latency (esp. for world saves / PVC)
chunk generation cost
entity cost
```

A value that works for one modpack may not for another. Only change what the
profile shows to be expensive.

## 3. JVM

- Start from modern JVM defaults; benchmark before adding a large flag set.
- The memory limit must include **non-heap** memory (metaspace, thread stacks,
  off-heap), not just `-Xmx`. If `-Xmx=2G`, size the container limit
  comfortably above (e.g. 3–4G) so the OOM-killer does not kill the JVM.
- GC tuning (e.g. G1 vs a concurrent collector for very large heaps) is
  workload-dependent; use spark/GC logs to decide.

## 4. World-generation workload

- Pre-generation stops on-the-fly chunk-gen MSPT spikes when players explore,
  but its value depends on how much new terrain is actually generated.
- Chunk generation cost is workload-dependent — measure before generating the
  whole world.

## 5. Entity/simulation workload

- Reduce what the server simulates *only after measuring* that entities are a
  top cost: view/simulation distance, mob-spawn-range, entity tick-rate,
  redstone/hopper behavior.
- Keep these as **runtime-specific configuration profiles** rather than a
  single global rule, because a modded colony world and a vanilla minigame
  differ.

## 6. Paper vs Folia

- **Paper** is the default.
- **Folia** (region multithreading) only after the workload proves region
  threads help (large, spread-out player counts on one world). Every plugin
  must explicitly support Folia; many Bukkit/Paper plugins will need rewriting
  or will not work — plan for that cost.

## 7. Modded-runtime tuning

- Maintain a **compatibility matrix** of optimization mods vs your runtimes
  (e.g. Lithium/VMP/C2ME/Server Core for Fabric; each must be tested).
- Benchmark each **runtime revision**, not individual folklore tweaks.

## 8. Capacity testing

Simulate load before launch and record the numbers:

```text
10 / 25 / 50 / 100 simulated users
record p50 / p95 / p99 MSPT
worldgen on/off
party clustering vs spread-out cases
```

## 9. Performance acceptance criteria

```text
TPS stays 20.0 at sustained load within the target player count
MSPT max stays under the defined threshold (default < 50 ms)
p95/p99 MSPT within the runtime's headroom target
no OOM-kill under the target load
```

---

## Java version matrix

Current Paper/Velocity distinction (re-verify against current Paper docs):

```text
Paper 1.20 … 1.21.11   -> Java 21
Paper 26.1+            -> Java 25
Velocity 4.x           -> Java 25
```

---

_Relocated here so the platform stays game-agnostic; this page is the
Minecraft repo's performance reference._
