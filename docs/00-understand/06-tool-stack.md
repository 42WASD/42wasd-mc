# The selected tool stack

| Layer | Tool | Why |
|---|---|---|
| Public proxy | **Velocity 4.0.0 stable** | Mature ecosystem; active 2026; strong Paper docs |
| Proxy JVM | **Java 25** | Required by current Velocity docs |
| Global TAB | **TAB 6.1.2** | All-in-one; Velocity support; MiniPlaceholders |
| Protocol translation | **ViaVersion + ViaBackwards 5.11.0** | Mature protocol bridge |
| Forge 1.20.1 proxy compat | **Ambassador + ProxyCompatibleForge** | Velocity + Forge 1.13–1.20.1 modern forwarding |
| Social/meta backend | **Nakama 3.40.0** | Friends, parties, presence, chat, matchmaking |
| Nakama production DB | **CockroachDB** | Supported production DB for Nakama |
| MC containers | **itzg/minecraft-server 2026.8.0** | Versions, loaders, modpacks |
| Proxy container | **itzg/mc-proxy `java25`** | Explicit Java 25 variant |
| Edge routing / external wake | **itzg/mc-router** | K8s discovery; 0↔1 wake; webhook; metrics |
| Persistent world orchestration | **custom World Controller + StatefulSet + PVC** | Persistent maps, invites, readiness, policy |
| Ephemeral session maps | **Agones** (optional) | Fleet/Allocation model |
| Public modded onboarding | **Modrinth Server Projects** | Install + launch into the server |
| Pack source/CI | **packwiz** (optional) | Git-friendly modpack definition |
| Source of truth | **Git + Kubernetes manifests** | Auditable, deterministic definitions |