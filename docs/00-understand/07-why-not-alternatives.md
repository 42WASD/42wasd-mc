# Why not the alternatives

## Shulker
A Kubernetes operator for dynamic Minecraft infra, conceptually very close. But its release cadence is less current than the selected components.

**Decision:** learn from its architecture, don't depend on it in v1, re-evaluate if maintenance resumes.

## CloudNet
A serious Minecraft-native cloud system, actively moving in 2026, but its 4.0 line was still in **release-candidate** during the audit. It's a good non-Kubernetes alternative. Not selected because this project is explicitly Kubernetes-first.

## SLS / SLS-LITE
Useful for smaller single-machine networks (launch/supervise local servers, matchmaking, transfers). Not selected because your Kubernetes cluster already exists, you want PVC-backed persistent worlds, RBAC, and scale-to-zero.

## AutoModpack
Useful in a trusted, closed modded community. But the client already needs AutoModpack, and installing executable mods remotely has trust/security implications. It can't hot-load a new classpath. For public onboarding, **Modrinth Server Projects is cleaner.**