# The selected tool stack

| Layer | Selected tool | Why it is selected |
|---|---|---|
| Public proxy | **Velocity 4.0.0 stable line** | Mature Minecraft ecosystem; active 2026 development; strong Paper docs |
| Proxy JVM | **Java 25** | Required by current Velocity docs |
| Global TAB | **TAB 6.1.2** | Current Aug 2026 release; all-in-one; Velocity support; MiniPlaceholders integration |
| Protocol translation | **ViaVersion 5.11.0 + ViaBackwards 5.11.0** | Current Jul 2026 release line; mature protocol bridge |
| Forge 1.20.1 proxy compatibility | **Ambassador + ProxyCompatibleForge** | PaperMC's documented path for Velocity + Forge 1.13–1.20.1 and modern forwarding |
| Social/meta backend | **Nakama 3.40.0** | Mature open-source game backend; friends, parties, presence, chat, matchmaking primitives |
| Nakama production DB | **CockroachDB** | Current Nakama config treats CockroachDB as required/supported production DB |
| Minecraft containers | **itzg/minecraft-server 2026.8.0 line** | Very active; supports versions/loaders/modpacks |
| Proxy container | **itzg/mc-proxy `java25` variant** | Convenient Velocity container; explicitly provides Java 25 variant |
| Edge hostname routing / external wake | **itzg/mc-router** | K8s discovery; StatefulSet scale 0↔1; webhook; metrics |
| Persistent world orchestration | **Custom World Controller + StatefulSet + PVC** | Exact fit for persistent maps, portals, invites, readiness and policy |
| Ephemeral session maps | **Agones, optional** | Mature Kubernetes game-server Fleet/Allocation model |
| Public modded onboarding | **Modrinth Server Projects** | Current 2026 flow installs required content and launches directly into the server |
| Pack source/CI | **packwiz, optional** | Git-friendly modpack definition and launcher/server update workflow |
| Dynamic infra source of truth | **Git + Kubernetes manifests** | Auditable, deterministic runtime/map definitions |