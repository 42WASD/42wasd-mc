# The one-sentence idea

Build a Minecraft network where **Velocity is the stable public proxy**, a small **World Controller** owns dynamic world lifecycle in Kubernetes, **Nakama** owns friends/parties/invites/presence, **TAB** renders global player information, **mc-router** optionally wakes hostname-addressed sleeping servers, and **Modrinth Server Projects** installs the correct modded runtime when a player cannot enter a world with their currently running client.

The mental model is:

```text
                         ┌──────────────────────────────┐
                         │       PLAYER / LAUNCHER      │
                         │ Vanilla client or Modrinth   │
                         └───────────────┬──────────────┘
                                         │
                                         ▼
                              ┌─────────────────────┐
                              │     mc-router       │
                              │ optional edge/wake  │
                              └──────────┬──────────┘
                                         │
                                         ▼
                              ┌─────────────────────┐
                              │     VELOCITY        │
                              │ public MC endpoint  │
                              └──────────┬──────────┘
                                         │
          ┌──────────────────────────────┼──────────────────────────────┐
          │                              │                              │
          ▼                              ▼                              ▼
 ┌────────────────┐             ┌────────────────┐             ┌────────────────┐
 │ Lobby / Paper  │             │ Vanilla / Map  │             │ Fantasy Forge  │
 │ always ready   │             │ GameServerSets │             │ 1.20.1 runtime │
 └────────────────┘             └────────────────┘             └────────────────┘

Velocity plugins / services
    │
    ├── TAB
    ├── ViaVersion + ViaBackwards
    ├── Ambassador (for Forge 1.13–1.20.1 backends)
    └── NetworkBridge (your small custom plugin)
             │
             ├───────────────► World Controller ─────► Kubernetes API
             │                         │
             │                         ├── wake / sleep GameServerSets
             │                         ├── wait for readiness
             │                         ├── register/unregister routes
             │                         └── random-map selection
             │
             └───────────────► Nakama
                                       │
                                       ├── friends
                                       ├── parties
                                       ├── invites
                                       ├── presence/status
                                       └── pending cross-runtime joins
```

The crucial rule is:

```text
Proxy compatibility != mod compatibility
Protocol translation != mod installation
Server lifecycle != social state
World routing != client runtime switching
```

---
