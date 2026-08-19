# Performance principles

Guidance on throughput, startup, and scaling for the dynamic network.

## Startup time is the UX

- Backend wake latency (Step 9/10) directly affects player experience.
- **Benchmark wake time per runtime** — a Forge runtime wakes slower than vanilla.
- Hold players with a clear "preparing map…" message during the wake (Step 10).

## Scale-to-zero wins on cost

- Sleeping maps cost ~nothing (0 replicas). Only pay when players are actually online.
- Tune idle timeout (see [routing state machine](routing-state-machine.md)) so you don't thrash.

## Throughput

- Proxy is the single entry point — scale it before it becomes the bottleneck.
- Keep backends on `ClusterIP`; only the proxy / router is exposed.
- Use resource limits so a loud map can't starve the cluster.

## Persistence

- World data on PVC (Step 9). Do **not** store world data in the container/pod.
- Repeated wake/sleep must not cause data loss (test in acceptance T5).

## Tooling principles

| Principle | Meaning |
|-----------|---------|
| Deterministic | same request → same routing decision (where sensible) |
| Idempotent | retrying a wake/transfer does not double-apply |
| Observable | every state change is logged/exported |
| Bounded | wake has a timeout, no infinite loops |

## See also

- [Step 9 — Scale-to-zero](../01-implement/step-09-scale-to-zero.md)
- [Step 18 — Agones](../01-implement/step-18-agones.md)
- [Operations: monitoring](../03-operations/monitoring.md)