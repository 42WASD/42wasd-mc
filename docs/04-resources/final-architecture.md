# Final architecture

The recommended end-state of the dynamic, runtime-aware Minecraft network after completing all 19 steps.

## Diagram

```mermaid
flowchart LR
  Client[Players] --> Edge[mc-router / public edge]
  Edge --> Proxy[Velocity proxy]
  Proxy --> Lobby[Lobby (static Paper)]
  Proxy --> Ctl[World Controller]
  Ctl --> K8s[Kubernetes]

  subgraph Static
    Lobby
    Sur[survival-main]
  end
  subgraph Dynamic
    B001[backrooms-001 scale-to-zero]
    B999[... more dynamic maps]
  end
  subgraph Fantasy
    F[fantasy-1.20.1-forge + Ambassador]
  end
  Ctl --> B001
  Ctl --> F
  Proxy --> B001
  Proxy --> F
  Proxy --> Sur
```

## Component summary

- **Edge**: mc-router routes the public host to the proxy, and handles edge wake.
- **Proxy**: Velocity 4.0.0, Java 25, modern forwarding.
- **Lobby / static backends**: always-running servers.
- **Dynamic maps**: scale-to-zero backends (Step 9) woken on demand by portals (Step 10).
- **Fantasy runtime**: Forge 1.20.1 backend via Ambassador / ProxyCompatibleForge (Step 13).
- **Controller**: owns runtime registry, map instances, routing/wake state, random selection.
- **Social**: Nakama identity (Step 5), friends/parties (Step 6), invites (Step 15).
- **Presence**: exact map presence via TAB (Steps 3, 11).
- **Protocol**: ViaVersion/Backwards (Step 4).
- **Packs**: Modrinth Server Projects (Step 14).
- **Edge/upload**: mc-router (Step 16), community map upload (Step 17).
- **Optional**: Agones ephemeral fleets (Step 18), AI proximity bot (Step 19).

## The core rule

"Required client runtime is standardized" — routing always checks a player's runtime against the target map's `runtimeId.compatibleClients`.

## Where to go next

- Review [reference contracts](../02-reference/index.md) for schemas & state machine.
- Review [operations](../03-operations/index.md) for backups, monitoring, security.
- Run the [acceptance test](../02-reference/acceptance-test.md) to validate.