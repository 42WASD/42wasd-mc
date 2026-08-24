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

---

# Phase — Route `minecraft.42base.com` to the prd paper-lobby via Velocity

## Intent

Point the public game domain **`minecraft.42base.com:25565`** at the **prd
paper-lobby** (through the Velocity proxy) instead of the dev tenant. The dev
`minecraft-demo` tenant is scaled to 0 so it no longer serves the domain.

## The path (unchanged relay, new backend)

```text
player -> minecraft.42base.com:25565
  -> Cloudflare / Melbicom VPS 89.36.162.171:25565   (DNS + tunnel)
  -> WireGuard wg0 10.200.0.2:30079                  (VPS DNAT :25565 -> wg0:30079)
  -> alpha NodePort 30079  -> Velocity proxy (prd)   (nodePort 30079)
  -> paper-lobby ClusterIP :25565                    (velocity.toml [servers] lobby)
```

The Melbicom relay was **kept unchanged**: its DNAT `:25565 -> 10.200.0.2:30079`
still stands. We simply **reused nodePort `30079`** in the cluster — it was
freed by scaling the dev `minecraft-demo` down — and gave it to the prd
**velocity** Service, which forwards to the paper-lobby.

## What was changed

### 1. Velocity Service: ClusterIP -> NodePort 30079 (`velocity/velocity.yaml`)

- `spec.type: ClusterIP` → `NodePort`.
- Added `nodePort: 30079` to the minecraft port (in the relay range
  `30000-30199` the VPS forwards).
- No iptables edit on the relay was needed because the range pass-through
  already covers `30079`.

### 2. Velocity ConfigMap: complete `velocity.toml` + `SKIP_DOWNLOAD_DEFAULTS=true`

- Set env `SKIP_DOWNLOAD_DEFAULTS=true` on the Deployment so the image **does
  not download its default `velocity.toml`**.
- Replaced the partial `[server]` fragment with a **complete, valid Velocity
  4.x config**: top-level keys + `[servers]` (`lobby` → the paper-lobby Service
  DNS name) + **empty `[forced-hosts]`** + `[advanced]` + `[query]`.

### 3. NetworkPolicy (`networkpolicy.yaml`)

- Added **`allow-proxy-to-paper-lobby`**: ingress to `app: paper-lobby` from
  `app: velocity` on `:25565`. Required because the namespace `default-deny`
  drops velocity→lobby at the destination; an egress allow on the source alone
  is insufficient (NetworkPolicies are two-way).

### 4. Dev tenant scaled to 0 (`ubuntu-server-iac`, ArgoCD-managed)

- `minecraft-demo` Deployment `replicas: 1 → 0` (world PVC retained).
- `minecraft-demo` Service `NodePort 30079 → ClusterIP` (frees the port for
  velocity). Applied via Git push + ArgoCD auto-sync (app
  `minecraft-demo`, repo `42WASD/ubuntu-server-iac`).

## Failure 1 — Velocity crash: `Server 'factions' for forced host ... does not exist`

After exposing the domain we restarted velocity and it crashed:

```text
[ERROR]: Server 'factions' for forced host 'factions.example.com' does not exist
[ERROR]: Server 'minigames' for forced host 'minigames.example.com' does not exist
[ERROR]: Your configuration is invalid. Velocity will not start up until the errors are resolved.
```

**Root cause (researched, authoritative):** the itzg `mc-proxy` image downloads
its **default `velocity.toml`** from `Shonz1/minecraft-default-configs`, which
ships a `[forced-hosts]` section with example hosts (`factions.example.com`,
`minigames.example.com`) referencing example servers. When we supplied only a
**partial** configmap (`[server]`/`[servers]`), the image merged its default's
`[forced-hosts]` against a config that had no `factions`/`minigames` servers →
Velocity rejects the config as invalid → crash-loop.

**Fix:** (a) `SKIP_DOWNLOAD_DEFAULTS=true` so the default is never pulled, and
(b) provide a **complete** `velocity.toml` that explicitly defines an **empty
`[forced-hosts]`** and a valid `[servers]`/`try`. Velocity requires a complete
config, not a fragment.

## Failure 2 — velocity can't reach paper-lobby (NetworkPolicy both-ways)

Velocity booted but `velocity -> paper-lobby` timed out:

```text
$ kubectl exec <velocity> -- bash -c 'echo > /dev/tcp/paper-lobby.../25565'
LOBBY UNREACHABLE
```

`default-deny` in `prd-games-42wasd-admin` blocks **ingress AND egress**. The
`allow-games-egress` policy lets the **source** (velocity) send, but the
**destination** (paper-lobby) had **no ingress allow**, so `default-deny`
dropped the packets at paper-lobby. Kubernetes NetworkPolicy is
**bidirectional**: both the sender and the receiver need a matching rule.

**Fix:** added `allow-proxy-to-paper-lobby` (ingress to `app: paper-lobby`
from `app: velocity` on `:25565`).

## Commands run

```bash
# === On alpha (jyao) ===
export PATH=$PATH:/var/lib/rancher/rke2/bin
export KUBECONFIG=/etc/rancher/rke2/rke2.yaml

# (dev tenant freed 30079 via ubuntu-server-iac + ArgoCD sync)

# velocity: NodePort + complete config
kubectl apply -f clusters/alpha/velocity/velocity.yaml
kubectl -n prd-games-42wasd-admin rollout restart deployment/velocity
kubectl -n prd-games-42wasd-admin rollout status deployment/velocity

# networkpolicy: allow proxy -> paper-lobby ingress
kubectl apply -f clusters/alpha/networkpolicy.yaml

# verify
kubectl get svc -n prd-games-42wasd-admin velocity   # NodePort 25565:30079/TCP
kubectl get netpol -n prd-games-42wasd-admin
kubectl -n prd-games-42wasd-admin exec deploy/velocity -- bash -c \
  'echo > /dev/tcp/paper-lobby.prd-games-42wasd-admin.svc.cluster.local/25565 && echo LOBBY-OPEN'
```

## Verified / observed

- `velocity` Service is `NodePort 25565:30079/TCP`; nodePort `30079` TCP OPEN on
  alpha.
- velocity pods `1/1 Running`, boot `Done (1.63s)!` with `Listening on 25565`,
  no config errors.
- `velocity -> paper-lobby` reachable via ClusterIP DNS (`LOBBY-OPEN`).
- Dev `minecraft-demo` scaled to 0; its Service back to ClusterIP; nodePort
  `30079` no longer held by dev.
- Netpol list: `default-deny`, `allow-cluster-dns`, `allow-games-egress`,
  `allow-games-ingress`, `allow-proxy-to-paper-lobby`.