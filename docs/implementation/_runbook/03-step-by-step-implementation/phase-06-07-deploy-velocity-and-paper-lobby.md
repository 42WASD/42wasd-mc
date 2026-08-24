---
phase: 03-step-by-step-implementation/deploy-velocity-and-paper-lobby
---

# Runbook — Phases 6 & 7: Deploy Velocity + the Paper lobby

Deployed the **Velocity proxy** (front door) and the **Paper lobby** (home
world) into `prd-games-42wasd-admin` on `alpha`. Both ended `1/1 Running`.
This write-up records the two real failure modes hit — a namespace default
LimitRange OOM, and a **Java 25 + Spark async-profiler native crash** — plus
the storage-controller non-issue that looked like the cause but wasn't.

## What was done

- **Velocity** (`clusters/alpha/velocity/velocity.yaml`):
  - Image `itzg/mc-proxy:java25` (the former `ghcr.io/papermc/velocity` tag
    did not resolve).
  - **Port corrected to `25565`.** itzg/mc-proxy sets `SERVER_PORT=25565` and
    ignores the `velocity.toml` `bind`, so the Service / containerPort /
    readiness probe must all target **25565**, not 25577.
- **Paper lobby** (`clusters/alpha/lobby/paper.yaml`):
  - Added a `10Gi` `nvme-fast` RWO PVC (`paper-lobby-data`).
  - Explicit `resources` (2Gi/4Gi) — without them the namespace LimitRange
    defaulted to `1Gi`, and world generation was **OOMKilled (exit 137)**.
  - **Java 21 image** `itzg/minecraft-server:2026.8.2-java21`.
- **Network policy** (`clusters/alpha/networkpolicy.yaml`):
  - Replaced the ad-hoc `allow-games-ingress` (was `ingress: [{}]` = allow-all
    to every pod) with a scoped policy: ingress to **velocity :25565** only.
  - Added velocity → internet egress 80/443 (jar download from
    `fill.papermc.io`); scoped to velocity pods only.

## Failure 1 — paper-lobby OOMKilled (exit 137)

The namespace LimitRange `container-defaults` sets `default.memory: 1Gi`.
Paper 1.21 world generation exceeds that and the container was OOM-killed
mid-`Preparing level "world"`, with no Java error (just exit 137).

**Fix:** explicit `resources.limits.memory: 4Gi` (under the LimitRange `max`
of 8Gi) in the container spec.

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

# Velocity — port fix
kubectl apply -f clusters/alpha/velocity/velocity.yaml

# Network policy
kubectl apply -f clusters/alpha/networkpolicy.yaml
```

## Verified / observed

- `velocity` 2× `1/1 Running`; Service endpoint `10.42.x:25565`; readiness
  green (probe hits the real SERVER_PORT).
- `paper-lobby` `1/1 Running`, 0 restarts, `Done (32.66s)!`, past the 37s
  Java 25 crash window on Java 21.
- `cockroachdb-0` and both `nakama` pods `1/1 Running`.
- Stale `kruise-daemon-config` (empty Helm-created) namespace deleted.