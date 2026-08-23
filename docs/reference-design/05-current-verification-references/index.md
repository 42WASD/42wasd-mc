# Current verification references

The following primary/current sources were checked for this edition. Re-audit them before major upgrades because Minecraft and its ecosystem change quickly.

1. **PaperMC — Velocity Getting Started**  
   https://docs.papermc.io/velocity/getting-started/  
   Current documentation states Java 25 is required.

2. **PaperMC — Velocity repository**  
   https://github.com/PaperMC/Velocity  
   Active proxy project and 4.x development/release history.

3. **PaperMC — Velocity Server Compatibility**  
   https://docs.papermc.io/velocity/server-compatibility/  
   Documents Paper/Fabric/Forge compatibility and Ambassador for Forge 1.13–1.20.1.

4. **PaperMC — Velocity Player Information Forwarding**  
   https://docs.papermc.io/velocity/player-information-forwarding/  
   Documents modern forwarding, Paper config, FabricProxy-Lite and ProxyCompatibleForge.

5. **PaperMC — Velocity Security**  
   https://docs.papermc.io/velocity/security/  
   Explains why forwarding is not a replacement for a firewall.

6. **Minekube Gate — repository**  
   https://github.com/minekube/gate

7. **Minekube Gate — Multi-Version Support**  
   https://gate.minekube.com/guide/multi-version

8. **Minekube Gate — Modded Servers**  
   https://gate.minekube.com/guide/modded-servers

9. **Minekube Gate — Compatibility**  
   https://gate.minekube.com/guide/compatibility

10. **TAB repository/releases**  
    https://github.com/NEZNAMY/TAB  
    https://github.com/NEZNAMY/TAB/releases

11. **TAB placeholders / Velocity MiniPlaceholders integration**  
    https://github.com/NEZNAMY/TAB/wiki/Placeholders

12. **ViaVersion releases**  
    https://github.com/ViaVersion/ViaVersion/releases

13. **ViaBackwards releases**  
    https://github.com/ViaVersion/ViaBackwards/releases

14. **Heroic Labs Nakama Release Notes**  
    https://heroiclabs.com/docs/nakama/getting-started/release-notes/  
    v3.40.0 released July 13, 2026.

15. **Heroic Labs Nakama Architecture**  
    https://heroiclabs.com/docs/nakama/getting-started/architecture/  
    Presence/status, streams and realtime architecture.

16. **Heroic Labs Nakama Server Configuration**  
    https://heroiclabs.com/docs/nakama/getting-started/configuration/  
    Current production database configuration guidance.

17. **itzg/docker-minecraft-server**  
    https://github.com/itzg/docker-minecraft-server

18. **itzg/docker-minecraft-server releases**  
    https://github.com/itzg/docker-minecraft-server/releases  
    2026.8.1 released August 19, 2026.

19. **itzg/docker-mc-proxy**  
    https://github.com/itzg/docker-mc-proxy  
    Documents Java 25 image variant.

20. **itzg/mc-router**  
    https://github.com/itzg/mc-router  
    Kubernetes/Docker discovery, hostname routing, edge-wake webhook behavior (native
    0↔1 auto-scale is StatefulSet-only, so waking a GameServerSet uses a custom webhook).

21. **Agones Fleet**  
    https://agones.dev/site/docs/reference/fleet/

22. **Agones GameServerAllocation**  
    https://agones.dev/site/docs/reference/gameserverallocation/

23. **Agones Fleet Autoscaling**  
    https://agones.dev/site/docs/advanced/scheduling-and-autoscaling/

24. **Modrinth — Introducing Server Projects**  
    https://modrinth.com/news/article/introducing-server-projects  
    2026 required-modpack server onboarding and direct launch flow.

25. **packwiz repository**  
    https://github.com/packwiz/packwiz

26. **CloudNet releases**  
    https://github.com/CloudNetService/CloudNet/releases  
    Useful alternative; 4.0 remained in RC status during this audit.

27. **Shulker repository**  
    https://github.com/jeremylvln/Shulker  
    Architecturally relevant Kubernetes Minecraft operator; re-check maintenance before adoption.

28. **itzg/mc-monitor**  
    https://github.com/itzg/mc-monitor  
    Minecraft status/ping probe + Prometheus/Influx metrics exporter used for readiness and per-server metrics.

29. **KEDA ScaledObject specification**  
    https://keda.sh/docs/reference/scaledobject-spec/  
    And OpenKruise "Gameservers Scale" guide showing a ScaledObject targeting a GameServerSet (`game.kruise.io/v1alpha1`).

30. **Velero**  
    https://velero.io/docs/  
    Scheduled PVC snapshots/restore, off-machine copy, restore-test hooks.

---

---

## Contents

- [Final architecture recommendation](final-architecture-recommendation/index.md)
