# Why several attractive projects are not the foundation

## Shulker

Shulker is conceptually very close to this project: a Kubernetes operator for dynamic Minecraft infrastructure.

However, its public release cadence is materially less current than the components selected above.

Decision:

```text
Learn from Shulker's architecture.
Do not make the first production version depend on it.
Re-evaluate if active maintenance resumes strongly.
```

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

AutoModpack is useful in a trusted, closed modded community.

But the client already needs AutoModpack, and installing/updating executable mods from a remote server has an explicit trust/security dimension.

It also cannot make Java hot-load a new classpath without restart.

Use it only if you intentionally operate a trusted fixed modded community.

For public onboarding, Modrinth Server Projects is cleaner.

---
