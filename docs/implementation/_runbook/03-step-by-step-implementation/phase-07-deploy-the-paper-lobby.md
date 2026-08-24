---
phase: 03-step-by-step-implementation/deploy-the-paper-lobby
---

# Runbook — Phase 7: Deploy the Paper lobby

Deployed the **Paper lobby** (the always-on home world behind Velocity) into
`prd-games-42wasd-admin` on `alpha`. It ended `1/1 Running`. This write-up
records the two real failure modes hit — a namespace default LimitRange OOM,
and a **Java 25 + Spark async-profiler native crash** — plus the
storage-controller non-issue that looked like the cause but wasn't.

## What was done

- **Paper lobby** (`clusters/alpha/lobby/paper.yaml`):
  - Added a `10Gi` `nvme-fast` RWO PVC (`paper-lobby-data`).
  - Explicit `resources` (`requests.memory: 2Gi`, `limits.memory: 8Gi`) plus
    `MEMORY=4G` heap — without them the namespace LimitRange defaulted to
    `1Gi`, and world generation was **OOMKilled (exit 137)**.
  - **Java 21 image** `itzg/minecraft-server:2026.8.2-java21`.
  - Recreate strategy (RWO single-node volume ⇒ rolling updates deadlock; see
    the storage-controller note below).

## Failure 1 — paper-lobby OOMKilled (exit 137)

The namespace LimitRange `container-defaults` sets `default.memory: 1Gi`.
Paper 1.21 world generation exceeds that and the container was OOM-killed
mid-`Preparing level "world"`, with no Java error (just exit 137).

**Fix:** explicit `resources.requests.memory: 2Gi` / `resources.limits.memory:
8Gi` (under the LimitRange `max` of 8Gi) and `MEMORY=4G` heap in the container
spec. The 4Gi pod limit originally used was too tight because the JVM heap is
only part of process memory (metaspace + thread stacks + native + GC overhead),
so heap `4G` + overhead exceeded it — hence `limits.memory: 8Gi` (2× heap) for
safe headroom.

## Failure 2 — JVM native SIGSEGV in Spark's async-profiler (Java 25)

After the OOM was fixed, the server got to `Done (37s)!` then crashed:

```
# SIGSEGV (0xb) at pc=0x0000000000000000
# JRE: Temurin-25.0.4+7
# Problematic frame:
# C [spark-...-libasyncProfiler.so.tmp+0x270e9]  VMThread::nativeThreadId(...)
# Current thread: JavaThread "Async-profiler Timer"
```

**Root cause (researched, authoritative):** lucko/spark **Issue #565
"Support Linux with Java25"** — Spark's bundled async-profiler native engine
crashes the JRE on **Java 25** on Linux the moment the profiler starts (which
Paper does ~37s after boot). The issue author confirms the intended JRE is
**Java 21**.

**Fix:** switch the image to the Java 21 build of the same release tag
(`2026.8.2-java21`). No `SPARK=false` workaround needed.

## Storage controller — NOT the problem (important)

The `verifyMount: device already mounted` / `can not mount, volume already
mounted` errors in the OpenEBS LVM plugin were **correct RWO enforcement**,
not a controller fault. During a Deployment RollingUpdate two pods briefly
coexist; the second one asks to mount the same single-node RWO volume the
first still holds, and the LVM plugin correctly refuses. On a one-node cluster
with an RWO PVC, a rolling update therefore deadlocks — always use a clean
delete → apply for such deployments.

## Commands run

```bash
# === On alpha (jyao) ===
export PATH=$PATH:$HOME/bin

# Paper-lobby — OOM fix + Java 21 (clean re-deploy, avoids RWO concurrent mount)
kubectl -n prd-games-42wasd-admin delete deployment paper-lobby
kubectl -n prd-games-42wasd-admin wait --for=delete pod -l app=paper-lobby --timeout=60s
kubectl apply -f clusters/alpha/lobby/paper.yaml
kubectl -n prd-games-42wasd-admin rollout status deployment/paper-lobby
```

## Verified / observed

- `paper-lobby` `1/1 Running`, 0 restarts, `Done (32.66s)!`, past the 37s
  Java 25 crash window on Java 21.
- Reached by velocity via `paper-lobby.prd-games-42wasd-admin.svc.cluster.local:25565`
  (`LOBBY-OPEN`; see the Phase 6 runbook).

---

# Phase — Import the missing multi-world data into the lobby PVC

## Symptom

The spawn system was not working. On every join Multiverse logged
`Failed to teleport player <name> on join: Failure{reason=NULL_LOCATION}`,
LobbyGames loaded **0 arenas**, and DecentHolograms couldn't resolve a
`spawn` world.

## Root cause — worlds missing from the PVC

The lobby PVC (`paper-lobby-data`, 10Gi) only contained the vanilla worlds
`world`, `world_nether`, `world_the_end`. The rest of the network's
**multi-world setup** — `spawn`, `creative_plots`, `Arcade`, `hub` — was
never copied into the PVC (the source had previously lived on a separate host
at `/home/jyao-42admin/42wasd-mc/world-data/`, a large server-data dir
gitignored by the repo). Multiverse-Core is configured (`join-destination:
spawn`) to send every joining player to the `spawn` world, so with that world
missing every spawn-related plugin failed:

```text
[Multiverse-Core] Failed to autoload world spawn: WORLD_FOLDER_INVALID
[Multiverse-Core] Failed to autoload world creative_plots: WORLD_FOLDER_INVALID
[Multiverse-Core] Failed to autoload world Arcade: WORLD_FOLDER_INVALID
[LobbyGames] Loaded 0 arenas!
[DecentHolograms] Cannot retrieve World from value spawn!
[20:06:39] [Multiverse-Core] Failed to teleport player jya0 on join: NULL_LOCATION
```

## Fix — rsync the missing worlds from the source host into the PVC

The authoritative full data dir is `/home/jyao-42admin/42wasd-mc/world-data/`
(gitignored; large binaries managed outside Git). The PVC is a host
`nvme-fast` LVM volume mounted at
`/var/lib/kubelet/pods/<pod-uuid>/volumes/kubernetes.io~csi/pvc-<id>/mount`.

Commands run (on alpha, via sudo):

```bash
# Locate the PVC host mount (matches pvc-c64d03bc-... = paper-lobby-data)
mount | grep pvc-c64d03bc

# Copy the 4 missing worlds and set ownership to the pod's UID (1000)
PVC=/var/lib/kubelet/pods/<pod-uuid>/volumes/kubernetes.io~csi/pvc-c64d03bc.../mount
SRC=/home/jyao-42admin/42wasd-mc/world-data
for d in spawn creative_plots Arcade hub; do
  rsync -a "$SRC/$d/" "$PVC/$d/"
done
chown -R 1000:1000 "$PVC/spawn" "$PVC/creative_plots" "$PVC/Arcade" "$PVC/hub"

# Restart the lobby so Multiverse loads the new worlds
kubectl -n prd-games-42wasd-admin rollout restart deployment/paper-lobby
kubectl -n prd-games-42wasd-admin rollout status deployment/paper-lobby
```

## Verified / observed

- `spawn` (129M), `creative_plots` (47M), `Arcade` (44M), `hub` (228K) now
  present in the PVC.
- Worlds autoload cleanly: `[WorldGuard] Loaded configuration for world 'spawn'`
  / `'creative_plots'`; `Prepared spawn area`.
- **`[LobbyGames] Loaded 7 arenas!`** (was 0).
- **`[DecentHolograms] Loaded 5 holograms!`**.
- No more `WORLD_FOLDER_INVALID`, `NULL_LOCATION`, or `Failed to teleport` in
  the logs.

## Note on the login plugin

The user originally asked to remove a login plugin (AuthMe) from the lobby PVC
— the `/login`/`/register` password plugin — but after the investigation chose
to **not remove** it and instead fix the spawn/world issue. AuthMe
(`AuthMe-5.7.0.jar`) and VerifyMC (email whitelist plugin) remain installed.