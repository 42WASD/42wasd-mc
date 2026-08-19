# Monitoring

Observability for the scale-to-zero dynamic network.

## What to monitor

| Signal | Tool | Why |
|--------|------|-----|
| Backend states (sleeping/running/error) | Controller metrics / K8s | detect wake thrash or stuck `starting` |
| Wake latency per runtime | Controller logs | startup is a UX metric |
| Player count per backend | Proxy / TAB / Nakama | scale + idle decisions |
| Proxy throughput | proxy metrics | bottleneck detection |
| DB status | CockroachDB health | social layer health |
| PVC usage | K8s | avoid full world volumes |

## Logging

- Structured logs from: proxy, backends, World Controller, Nakama, mc-router.
- Route to a log backend and correlate by `mapId`, `runtimeId`, `playerId`.

## Alerts (suggested)

- `starting` lasting beyond the wake timeout → alert.
- A backend stuck in `error` → alert.
- Proxy down / unreachable → high priority alert.
- Disk/volume near full on any world → alert.

## Dashboard

- Show: running/sleeping counts per runtime, active players per map, wake success rate, wake p95 latency.

## See also

- [Performance principles](../02-reference/performance-principles.md)
- [Acceptance test](../02-reference/acceptance-test.md)