# Implement the platform — 19 steps

Follow these steps in order. Each is a self-contained increment: it has a **goal**, the **tasks** to do, and an **acceptance check** to confirm it works before moving on.

The order deliberately proves one contract at a time — you never debug multiple unknowns at once.

| Step | Title | Builds on |
|---:|---|---|
| [1](step-01-velocity-lobby.md) | Velocity + static Paper lobby | — |
| [2](step-02-forwarding-isolation.md) | Secure forwarding + backend isolation | 1 |
| [3](step-03-tab.md) | TAB | 2 |
| [4](step-04-protocol.md) | ViaVersion / ViaBackwards | 2 |
| [5](step-05-nakama-identity.md) | Nakama identity mapping | 1 |
| [6](step-06-friends-parties.md) | Friends + parties | 5 |
| [7](step-07-join.md) | Second static backend + `/join` | 6 |
| [8](step-08-world-controller.md) | World Controller | 2 |
| [9](step-09-scale-to-zero.md) | Persistent StatefulSet scale-to-zero map | 8 |
| [10](step-10-portal-wake-transfer.md) | Portal → wake → transfer | 9 |
| [11](step-11-tab-exact.md) | Exact map presence + TAB | 10 |
| [12](step-12-random-map.md) | Random compatible map | 11 |
| [13](step-13-fantasy-forge.md) | Fantasy Forge runtime + Ambassador + ProxyCompatibleForge | 2 |
| [14](step-14-modrinth.md) | Modrinth Server Project | 13 |
| [15](step-15-cross-runtime-invite.md) | Cross-runtime invite | 14 |
| [16](step-16-mc-router.md) | mc-router edge wake | 10 |
| [17](step-17-map-upload.md) | Community map upload pipeline | 12 |
| [18](step-18-agones.md) | Agones ephemeral fleet (optional) | 10 |
| [19](step-19-ai-proximity.md) | AI proximity bot | 11 |

## Prerequisite: understand first

If you have not read the [understand](../00-understand/index.md) section, at minimum read these before starting:

- [Runtime classes](../00-understand/04-runtime-classes.md)
- [The seven layers](../00-understand/03-seven-layers.md)

## Naming convention (Step 1 prerequisite)

Use stable identifiers:

```text
Namespace:         minecraft (game servers), minecraft-system (infrastructure)
Public host:       play.example.com
Runtime IDs:       vanilla-current, backrooms-current, fantasy-1.20.1-forge
Backend logical:   lobby-1, survival-main, backrooms-001, fantasy-kingdom-001
```

Never use display names as primary keys.