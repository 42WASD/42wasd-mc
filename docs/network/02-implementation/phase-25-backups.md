# Phase 25 — Backups

Persistent worlds:

```text
PVC
  ↓
Minecraft save / quiesce
  ↓
snapshot/backup
  ↓
off-machine copy
```

Do not call a backup successful merely because a file exists. **Test restores.**

Minimum test:

```text
[ ] delete disposable test instance
[ ] restore world to new PVC
[ ] boot server
[ ] verify known structures/player data
```

Also back up:

```text
CockroachDB
runtime/map Git repo
Nakama runtime config
Velocity config
secrets through your secret-management process
```