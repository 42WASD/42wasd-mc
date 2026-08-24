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
provides **Kubernetes resource backup** plus **supported volume backup/
snapshot** flows (via CSI snapshot, data mover, or object store), running on a
schedule with retention and **backup/restore hooks** (for the Minecraft
save/quiesce step).

> **Restore testing is our process, not an automatic Velero feature.** Velero
> can *restore* resources/volumes, but whether a restore is correct — and
> whether the backup is actually durable off-cluster — depends on your
> CSI/data-mover/object-store arrangement. "Restore drills + integrity
> verification" is a **42WASD runbook/CI process** scheduled on top of Velero,
> not something Velero guarantees by itself.

The World Controller still decides *when* a world is quiescent to back up;
Velero owns the snapshot/restore mechanics and the off-machine copy to object
storage.

---
