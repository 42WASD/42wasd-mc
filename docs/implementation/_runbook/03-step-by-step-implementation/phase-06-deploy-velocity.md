---
phase: 03-step-by-step-implementation/deploy-velocity
---

# Runbook — Phase 6: Deploy Velocity

Deployed the **Velocity proxy** (the front door for every game connection)
into `prd-games-42wasd-admin` on `alpha`, then exposed it on nodePort `30079`
and routed the public domain `minecraft.42base.com:25565` to the prd stack.
This write-up records the real failure modes hit along the way — the
`itzg/mc-proxy` **default `velocity.toml`** causing a config-reject crash-loop,
and the **NetworkPolicy both-ways** gotcha that made velocity unable to reach
the lobby.

## What was done

- **Velocity Deployment** (`clusters/alpha/velocity/velocity.yaml`):
  - Image `itzg/mc-proxy:java25` (the former `ghcr.io/papermc/velocity` tag
    did not resolve).
  - **Port corrected to `25565`.** itzg/mc-proxy sets `SERVER_PORT=25565` and
    ignores the `velocity.toml` `bind`, so the Service / containerPort /
    readiness probe must all target **25565**, not 25577.
- **Velocity Service: ClusterIP -> NodePort 30079**:
  - Added `nodePort: 30079` (in the game-edge relay range `30000-30199` the
    VPS forwards).
  - No iptables edit on the relay was needed — the range pass-through already
    covers `30079`.
- **Velocity ConfigMap: complete `velocity.toml` + `SKIP_DOWNLOAD_DEFAULTS=true`**:
  - Env `SKIP_DOWNLOAD_DEFAULTS=true` stops the image downloading its default
    `velocity.toml` (which ships a bad `[forced-hosts]`).
  - Replaced the partial fragment with a **complete, valid Velocity 4.x
    config**: top-level keys + `[servers]` (`lobby` → the paper-lobby Service
    DNS name) + **empty `[forced-hosts]`** + `[advanced]` + `[query]`.
- **Network policy** (`clusters/alpha/networkpolicy.yaml`):
  - Replaced the ad-hoc `allow-games-ingress` (was `ingress: [{}]` = allow-all
    to every pod) with a scoped policy: ingress to **velocity :25565** only.
  - Added velocity → internet egress 80/443 (jar download from
    `fill.papermc.io`); scoped to velocity pods only.
  - Added **`allow-proxy-to-paper-lobby`**: ingress to `app: paper-lobby`
    from `app: velocity` on `:25565`. See Failure 2 below.

## The routing path (relay unchanged, new backend)

```text
player -> minecraft.42base.com:25565
  -> Cloudflare / Melbicom VPS 89.36.162.171:25565  (DNS + tunnel)
  -> WireGuard wg0 10.200.0.2:30079                  (VPS DNAT :25565 -> wg0:30079)
  -> alpha NodePort 30079  -> Velocity proxy (prd)   (nodePort 30079)
  -> paper-lobby ClusterIP :25565                    (velocity.toml [servers] lobby)
```

The Melbicom relay was **kept unchanged**: its DNAT `:25565 -> 10.200.0.2:30079`
still stands. We simply **reused nodePort `30079`** in the cluster — it was
freed by scaling the dev `minecraft-demo` tenant down — and gave it to the prd
**velocity** Service.

## Dev tenant scaled to 0 (`ubuntu-server-iac`, ArgoCD-managed)

- `minecraft-demo` Deployment `replicas: 1 → 0` (world PVC retained).
- `minecraft-demo` Service `NodePort 30079 → ClusterIP` (frees the port for
  velocity). Applied via Git push + ArgoCD auto-sync (app `minecraft-demo`,
  repo `42WASD/ubuntu-server-iac`).

## Failure 1 — Velocity crash: `Server 'factions' for forced host ... does not exist`

After exposing the domain we restarted velocity and it crashed:

```text
[ERROR]: Server 'factions' for forced host 'factions.example.com' does not exist
[ERROR]: Server 'minigames' for forced host 'minigames.example.com' does not exist
[ERROR]: Your configuration is invalid. Velocity will not start up until the errors are resolved.
```

**Root cause (researched, authoritative):** the itzg `mc-proxy` image downloads
its **default `velocity.toml`** from `Shonz1/minecraft-default-configs`, which
ships a `[forced-hosts]` section with example hosts (`factions.example.com`,
`minigames.example.com`) referencing example servers. When we supplied only a
**partial** configmap (`[server]`/`[servers]`), the image merged its default's
`[forced-hosts]` against a config that had no `factions`/`minigames` servers →
Velocity rejects the config as invalid → crash-loop.

**Fix:** (a) `SKIP_DOWNLOAD_DEFAULTS=true` so the default is never pulled, and
(b) provide a **complete** `velocity.toml` that explicitly defines an **empty
`[forced-hosts]`** and a valid `[servers]`/`try`. Velocity requires a complete
config, not a fragment.

## Failure 2 — velocity can't reach paper-lobby (NetworkPolicy both-ways)

Velocity booted but `velocity -> paper-lobby` timed out:

```text
$ kubectl exec <velocity> -- bash -c 'echo > /dev/tcp/paper-lobby.../25565'
LOBBY UNREACHABLE
```

`default-deny` in `prd-games-42wasd-admin` blocks **ingress AND egress**. The
`allow-games-egress` policy lets the **source** (velocity) send, but the
**destination** (paper-lobby) had **no ingress allow**, so `default-deny`
dropped the packets at paper-lobby. Kubernetes NetworkPolicy is
**bidirectional**: both the sender and the receiver need a matching rule.

**Fix:** added `allow-proxy-to-paper-lobby` (ingress to `app: paper-lobby`
from `app: velocity` on `:25565`).

## Commands run

```bash
# === On alpha (jyao) ===
export PATH=$PATH:/var/lib/rancher/rke2/bin
export KUBECONFIG=/etc/rancher/rke2/rke2.yaml

# (dev tenant freed 30079 via ubuntu-server-iac + ArgoCD sync)

# velocity: NodePort + complete config
kubectl apply -f clusters/alpha/velocity/velocity.yaml
kubectl -n prd-games-42wasd-admin rollout restart deployment/velocity
kubectl -n prd-games-42wasd-admin rollout status deployment/velocity

# networkpolicy: allow proxy -> paper-lobby ingress
kubectl apply -f clusters/alpha/networkpolicy.yaml

# verify
kubectl get svc -n prd-games-42wasd-admin velocity   # NodePort 25565:30079/TCP
kubectl get netpol -n prd-games-42wasd-admin
kubectl -n prd-games-42wasd-admin exec deploy/velocity -- bash -c \
  'echo > /dev/tcp/paper-lobby.prd-games-42wasd-admin.svc.cluster.local/25565 && echo LOBBY-OPEN'
```

## Verified / observed

- `velocity` Service is `NodePort 25565:30079/TCP`; nodePort `30079` TCP OPEN on
  alpha.
- velocity pods `2× 1/1 Running`, boot `Done (1.63s)!` with
  `Listening on 25565`, no config errors.
- `velocity -> paper-lobby` reachable via ClusterIP DNS (`LOBBY-OPEN`).
- Dev `minecraft-demo` scaled to 0; its Service back to ClusterIP; nodePort
  `30079` no longer held by dev.
- Netpol list: `default-deny`, `allow-cluster-dns`, `allow-games-egress`,
  `allow-games-ingress`, `allow-proxy-to-paper-lobby`.