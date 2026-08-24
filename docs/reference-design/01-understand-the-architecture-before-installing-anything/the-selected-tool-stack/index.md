# The selected tool stack

| Layer | Selected tool | Why it is selected |
|---|---|---|
| Public proxy | **Velocity 4.0.0 stable line** | Mature Minecraft ecosystem; active 2026 development; strong Paper docs |
| Proxy JVM | **Java 25** | Required by current Velocity docs |
| Global TAB | **TAB 6.1.2** | Current Aug 2026 release; all-in-one; Velocity support; MiniPlaceholders integration |
| Protocol translation | **ViaVersion 5.11.0 + ViaBackwards 5.11.0** | Current Jul 2026 release line; mature protocol bridge |
| Forge 1.20.1 proxy compatibility | **Ambassador + ProxyCompatibleForge** | PaperMC's documented path for Velocity + Forge 1.13–1.20.1 and modern forwarding |
| Social/meta backend | **Nakama 3.40.0** | Mature open-source game backend; friends, parties, presence, chat, matchmaking primitives. Also the **OAuth-first identity anchor** (Discord/Google social login), with the Minecraft UUID linked as a runtime binding |
| Nakama production DB | **CockroachDB** | Nakama requires a Postgres-wire-compatible DB; CockroachDB is our production pick (PostgreSQL is also supported) |
| Minecraft containers | **itzg/minecraft-server 2026.8.1 line** | Very active; supports versions/loaders/modpacks |
| Proxy container | **itzg/mc-proxy `java25` variant** | Convenient Velocity container; explicitly provides Java 25 variant |
| Edge hostname routing / external wake | **itzg/mc-router** | K8s service discovery; edge wake via webhook (native 0↔1 auto-scale is StatefulSet-only); metrics |
| Persistent world orchestration | **Custom World Controller** | Exact fit for persistent maps, portals, invites, readiness and policy |
| Persistent world workload | **OpenKruiseGame `GameServerSet` + PVC** | CNCF-incubated game-server workload; in-place update, per-world ops protection, scale-to-zero |
| Ephemeral session maps | **Agones, optional** | Mature Kubernetes game-server Fleet/Allocation model |
| Public modded onboarding | **Modrinth Server Projects** | Current 2026 flow can install required content and launch directly into the server |
| Player client (launcher) | **AstralRinth** | Offline/cracked-capable Modrinth App fork; pinned in `42WASD/AstralRinth` (our own tracked fork) |
| Pack source/CI | **packwiz, optional** | Git-friendly modpack definition and launcher/server update workflow |
| Minecraft readiness probe & metrics | **itzg/mc-monitor** | Maintained status/ping probe (`status` subcommand); exports online count, latency, MOTD to Prometheus/Influx — shared source for readiness and perf metrics |
| Scale trigger (idle / player-count) | **KEDA, optional** | CNCF-graduated; `ScaledObject` → HPA fires the GameServerSet 0↔1 transition; safe-to-stop decision stays in World Controller |
| World/DB backup & restore | **Velero** | Apache-2.0, CNCF-governed; scheduled PVC snapshots + off-machine copy + restore-test hooks |
| Dynamic infra source of truth | **Git + Kubernetes manifests** | Auditable, deterministic runtime/map definitions |

---

## Why every container runs its own JVM (and why that is correct)

A natural question is: *"every server/proxy runs a JVM — is that wasteful, and
can we share one JVM across them?"* The short answer is **no — do not share a
JVM**, and this is standard, intended container behavior:

- Each Minecraft server and the proxy is a **separate Java process** that must
  be independently started, stopped, scaled, restarted and memory-limited. A
  single shared JVM cannot isolate one world's crash, GC pause, or OOM from
  another; process isolation is the whole point.
- The JVM is small relative to a world: a proxy needs ~1GB for 1000 players,
  and a modded server's cost is dominated by the world/mod simulation, not the
  JVM base overhead. Sharing the JVM saves little and sacrifices isolation.
- Kernel sharing is handled by the **container runtime** (namespaces/cgroups);
  JVM/class-sharing (CDS archives) can reduce *cold-start* time inside a
  single process, but it does **not** mean multiple servers share one runtime.
- LXD/system-containers share a kernel, not an application runtime. Minecraft
  servers are not like stateless functions; each needs a stable, isolated JVM
  on its own. If resource density matters, prefer **right-sizing requests/
  limits and scale-to-zero** (already in this design) over trying to share a
  JVM.

## GitOps: applying the Git source of truth

"Git is the source of truth" is realized with a **GitOps controller** —
**Argo CD** (or Flux) reconciles the cluster to the manifests in Git:

```text
Git repo (runtime/map manifests, policy)
   ↓
Argo CD (watches the repo, applies to cluster)
   ↓
cluster converges to desired state
```

- Argo CD watches the Git repo and automatically applies changes, drift
  (someone `kubectl apply`s something not in Git) is corrected back to the
  repo, and every change is a reviewable commit.
- The **custom World Controller** remains the live *runtime* authority for
  dynamic map instances (it creates/sleeps GameServerSets on demand), while
  Argo CD owns the *static* infrastructure (namespaces, the World Controller
  itself, proxy, monitoring, CRDs). The two coexist: Argo CD keeps the
  platform definitions from drifting; the World Controller manages the
  on-demand world lifecycle on top of it.
