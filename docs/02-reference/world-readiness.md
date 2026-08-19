# World readiness contract

A transfer must **not** happen until a world/backend is fully ready. This contract defines what "ready" means.

## Definition of ready

A backend is ready to accept players when all of these hold:

1. The pod is scheduled and the container is running (Java started).
2. The world is loaded on the persistent volume.
3. The minecraft port is **open** and a server ping/ready probe succeeds.
4. For Forge runtimes: the Ambassador is registered and forwarding is up.
5. The controller has flipped state from `starting` → `running`.

## Readiness probe (sketch)

```yaml
readinessProbe:
  exec:
    command: ["/bin/sh", "-c", "mcstatus localhost:25565 status >/dev/null 2>&1"]
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
```

For Forge runtimes, also wait for the Ambassador to report ready.

## Contract rule

- The proxy must **never** transfer a player to a backend that is not `running`.
- During `starting`, the player is held in the lobby/wait state (Step 10).
- On timeout → `error` and return the player (no infinite hang).

## Enforcing the wake/wait gate

The readiness signal feeds the transfer decision in [routing-state-machine](routing-state-machine.md). The controller blocks the handoff until `ready == true`.

## See also

- [Step 9 — Scale-to-zero](../01-implement/step-09-scale-to-zero.md)
- [Step 10 — Portal wake flow](../01-implement/step-10-portal-wake-transfer.md)