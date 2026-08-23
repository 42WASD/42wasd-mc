---
phase: 03-step-by-step-implementation/build-the-world-controller
---
# Maintained-tool fills for the World Controller operator

## What was done

Following a 2026-08 online audit of the operator landscape, added three
actively-maintained tools to the reference design to reduce the custom
World Controller/NetworkBridge code. Each maps to a specific custom piece the
design was hand-rolling:

- **itzg/mc-monitor** → the Minecraft `status/ping` readiness probe and the
  per-server metrics (online, latency, MOTD) exported to Prometheus. Verified
  active: Docker Hub updated within days; v0.17.1 current.
- **KEDA** → the idle/player-count scale-to-zero **trigger** (`ScaledObject` →
  HPA on the GameServerSet). CNCF-graduated. The safe-to-stop decision
  (reservations, draining, maintenance) intentionally stays custom in the
  World Controller.
- **Velero** → the PVC snapshot/restore/schedule + off-machine copy + restore
  test half of the backup pipeline. Apache-2.0, CNCF-governed.

Also confirmed **Argo CD is already owned** by `42WASD/ubuntu-server-iac` (the
host platform), so no GitOps applier was added here. AutoModpack and Gate were
already evaluated and rejected with documented reasons in the reference design.

## Commands

```bash
# Edit target pages (all under docs/reference-design/)
#   04/.../world-readiness-contract          -> mc-monitor (readiness contract)
#   03/.../build-the-world-controller        -> mc-monitor (two-stage readiness)
#   03/.../monitoring                        -> mc-monitor (shared metrics source)
#   03/.../add-idle-sleep                    -> KEDA (scale trigger)
#   03/.../add-mc-router                      -> KEDA (optional edge-wake trigger)
#   03/.../backups                           -> Velero (backup operator)
#   01/.../the-selected-tool-stack           -> added 3 rows
#   02/.../capability-cheat-sheet            -> added 3 rows

# Regenerate nav + implementation index from SSOT (cwd is projects/)
python3 /home/jyao/42wasd-mc/scripts/docs/docs-generate-nav.py
python3 /home/jyao/42wasd-mc/scripts/docs/docs-generate-implementation.py

# Full verification pipeline (validate -> tests -> strict build)
bash /home/jyao/42wasd-mc/scripts/docs/verify.sh
# => VERIFY OK
```

## Verified

- `verify.sh` reports `VERIFY OK` (validate -> 7 pytest -> strict mkdocs build).
- Generated nav and implementation index regenerated cleanly.
- No new phases added to `_sequence.yaml`; the additions strengthen existing
  sections (build-the-world-controller, add-idle-sleep, add-mc-router,
  backups, monitoring, world-readiness-contract).

---