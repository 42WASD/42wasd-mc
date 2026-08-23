# Backups

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

Do not call a backup successful merely because a file exists.

Test restores.

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

---

## Use a maintained backup operator

The PVC snapshot/restore/schedule half of this pipeline is owned by a
maintained operator — **Velero** — rather than hand-rolled scripts. Velero
backs up cluster objects and PVCs, runs on a schedule with retention, and
supports pre/post hooks (for the Minecraft save/quiesce step) and restore
testing. It is Apache-2.0 and CNCF- governed.

The World Controller still decides *when* a world is quiescent to back up; Velero
owns the snapshot/restore mechanics and the off-machine copy to object storage.

---
