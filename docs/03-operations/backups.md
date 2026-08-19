# Backups

Back up the two kinds of state that must survive: **world data** and **database (Nakama/CockroachDB)**.

## World data (PVC)

Worlds live on a PVC (scale-to-zero, Step 9). Back up:

```bash
# snapshot the PVC (example: cloud/CSI volume snapshot)
kubectl snapshot volume --name backrooms-001-world \
  --namespace minecraft --class <snapshot-class>
```

- Snapshot **periodically** (e.g. nightly) and before any upgrade (see [upgrade-policy](../02-reference/upgrade-policy.md)).
- Keep last N snapshots; do not keep everything forever.
- **Test a restore** periodically — an untested backup is not a backup.

## Database (Nakama / CockroachDB)

- Use CockroachDB's backup feature to a persistent/bucket store.
- Back up on the same schedule as world data.

## What else

- Proxy config and runtime definitions (tracked in the repo).
- Forwarding secret and other secrets are restored from your secret store, not the backup.

## Restore runbook

1. Restore the world PVC snapshot.
2. Restore the DB (Nakama identity + friendships).
3. Verify identity mapping still resolves (Step 5 acceptance).

## See also

- [Step 9 — Scale-to-zero](../01-implement/step-09-scale-to-zero.md)
- [Upgrade policy](../02-reference/upgrade-policy.md)