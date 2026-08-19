# Phase 22 — Add Agones for session worlds

Install Agones when you have a workload such as:

```text
Backrooms run
Dungeon run
Minigame
Disposable generated challenge
```

Use:

```text
Fleet
    ↓
Ready GameServers
    ↓
GameServerAllocation
    ↓
Allocated session
    ↓
session ends
    ↓
shutdown/replacement
```

A Fleet Autoscaler can keep a buffer of ready capacity.

Do **not** replace your persistent PVC-backed survival worlds with this unless you intentionally redesign their persistence model.