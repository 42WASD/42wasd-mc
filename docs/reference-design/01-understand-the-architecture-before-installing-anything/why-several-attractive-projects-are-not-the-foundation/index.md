# Why several attractive projects are not the foundation

Most projects on this page are **not** the foundation. The one exception is
**OpenKruiseGame**, which appears here only to contrast with `Shulker` but is
**selected** — it is clearly marked below.

## Shulker

Shulker is conceptually very close to this project: a Kubernetes operator for dynamic Minecraft infrastructure.

However, its public release cadence is materially less current than the components selected above. As of the 2026-08 audit, its latest release is **v0.13.0 (2025-04-05)** — still pre-1.0 (`0.x`) and with no release in over a year. Its operator pins `itzg/minecraft-server`/`itzg/mc-proxy` **`java21`** images, while this project targets the **Java 25 / 2026.8.x** line.

Decision:

```text
Learn from Shulker's architecture.
Do not make the first production version depend on it.
Re-evaluate if active maintenance resumes strongly.
```

The alternative is **not** a generic GitOps tool: it is a **custom World Controller** (which owns the product semantics: portals, invites, readiness, policy) driving an **OpenKruiseGame `GameServerSet`** workload (which owns the stateful game-server primitive). This keeps the foundation actively maintained without outsourcing bespoke behavior.

---

## OpenKruiseGame — SELECTED (not rejected)

> ✅ **Selected as the persistent-world workload.** This is the exception on this
> page: OKG is *not* a rejected candidate — it is the stateful game-server
> primitive this design uses (see `install-openkruisegame`,
> `build-the-world-controller`, `add-idle-sleep`). It is listed here only to
> contrast with `Shulker` above.

OpenKruiseGame (OKG) is an open-source game-server workload project — a sub-project of OpenKruise, which is a CNCF project. It is actively maintained and specialized for stateful game servers.

It is selected as the **persistent-world workload** here, but it is **not** a "Minecraft-branded" operator: it does not implement portal routing, invites, world-readiness contracts, or routing policy. Those stay in the custom World Controller.

What it provides:

```text
GameServerSet workload (stable per-server identity)
in-place update: only for supported/eligible pod-field changes (unsupported
   changes fall back to pod recreation, so the world/PVC lifecycle must stay
   safe under both paths)
per-server opsState protection from autoscaling/update
PVC-backed persistent worlds (VolumeClaimTemplates)
scale-to-zero
```

It is chosen over Shulker because it is actively maintained, Apache-2.0, and gives a permissive stateful workload primitive the World Controller drives — without adopting Shulker's dormant pre-1.0 API.

---

## CloudNet

CloudNet is a serious Minecraft-native cloud system and is actively moving in 2026.

However, its 4.0 line is still in **release-candidate** status during this audit.

It is a good alternative when you want:

```text
Minecraft-native cloud manager
templates
dynamic services
less Kubernetes-specific ownership
```

It is not selected because this project is explicitly Kubernetes-first.

---

## SLS / SLS-LITE

SLS-LITE is actively useful for a smaller single-machine network and can launch/supervise local Java servers, perform matchmaking/queues, and transfer players.

This makes it interesting for a non-Kubernetes deployment.

It is not the selected foundation because:

```text
your Kubernetes cluster already exists
you want persistent PVC-backed worlds
you want infrastructure policy / RBAC
you want scale-to-zero controlled by K8s
```

---

## AutoModpack

AutoModpack can auto-sync mods from a server to joining clients, but it is only
a good fit for a trusted, closed modded community. Three reasons:

- **The client must already have AutoModpack installed.** It can only download
  and apply mods after AutoModpack itself is running, so a vanilla client gains
  nothing from it — the setup is not seamless for new players.
- **It pushes executable code to players.** Minecraft mods (`.jar` files) are
  executable code. Letting a remote server download and run them on a player's
  machine is an explicit trust/security decision, not an automatic convenience.
- **Java cannot hot-load a new classpath.** Even after the mods are downloaded,
  they cannot be injected into an already-running game; the player must fully
  restart their Minecraft client to apply them.

Use it only if you intentionally operate a trusted, fixed modded community.

For public onboarding, **Modrinth Server Projects** is cleaner: the launcher
installs the required pack before the game starts, so nothing is fetched from a
remote server at runtime.

---
