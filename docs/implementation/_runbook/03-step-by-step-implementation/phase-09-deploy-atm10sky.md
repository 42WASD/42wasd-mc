---
phase: 03-step-by-step-implementation/deploy-the-forge-1-20-1-fantasy-runtime
---

# Phase 9 — Deploy the ATM10SKY modded server

Second game runtime in the network: **All the Mods 10: To the Sky** (server
pack 2.2.0), 322 mods on **NeoForge 21.1.250 / Minecraft 1.21.1**.

Deliberately **standalone** (NodePort `30080`), not behind the Velocity proxy.

## Why not behind Velocity

- Velocity's documented modded support covers **Forge >1.20.2**; NeoForge is a
  fork and there is no explicit compatibility guarantee.
- Our `velocity.toml` sets `player-info-forwarding-mode = "none"`, so the proxy
  forwards no identity — it adds a failure domain across 322 mods and buys
  nothing.
- The UAE relay already DNATs `30000-30199`, so a NodePort reaches players the
  same way the lobby's port does.

## Decision: no custom image

The `itzg/minecraft-server` image already running the lobby supports NeoForge
natively (`TYPE=NEOFORGE` + `NEOFORGE_VERSION`). The modpack is **data**, not
code, so it belongs on the PVC rather than baked into an image. A thin
`FROM itzg/... COPY pack` image would force a ~500 MB rebuild per pack update
and gain only digest pinning, which `NEOFORGE_VERSION` + the file ID already
give us.

## Prerequisite: quota (iac repo)

The namespace could not host this server. See `ubuntu-server-iac` commit
`a85a440` — `infra/kubernetes/platform/quotas/games.yaml` and
`infra/kubernetes/platform/limitranges/games.yaml`:

```
limits.memory         16Gi -> 32Gi    (had 3 GiB free; need ~14)
requests.memory        8Gi -> 16Gi
limits.cpu               8 -> 16
requests.cpu             4 -> 8
requests.storage      200Gi -> 300Gi
persistentvolumeclaims   8 -> 12
LimitRange max.memory  8Gi -> 16Gi    <- would have REJECTED the pod outright
```

The LimitRange was the hard blocker: `max.memory: 8Gi` means the apiserver
rejects any single container asking for more, regardless of quota headroom.

## Manifests (`clusters/alpha/atm10sky/`)

| file | contents |
|---|---|
| `atm10sky.yaml` | PVC 40Gi (`nvme-fast`), NodePort Service `30080`, Deployment |
| `networkpolicy.yaml` | `allow-atm10sky-ingress` (:25565), `allow-atm10sky-egress` (HTTPS/HTTP for bootstrap) |
| `kustomization.yaml` | aggregates the two |

Key deployment settings:

```yaml
TYPE=NEOFORGE, VERSION=1.21.1, NEOFORGE_VERSION=21.1.250
NEOFORGE_INSTALLER=/data/.bootstrap/neoforge-21.1.250-installer.jar
ONLINE_MODE=FALSE          # cracked/offline clients, same as the lobby
LEVEL_TYPE=skyblockbuilder:skyblock
ALLOW_FLIGHT=TRUE, MAX_TICK_TIME=180000
ENABLE_RCON=true, RCON_PASSWORD=atm10sky-rcon-internal
PUID/PGID=10000, MEMORY=8G
runAsUser/runAsGroup/fsGroup=10000   # NOT 1000 (see Incident 2)
```

`strategy: Recreate` — RWO PVC on one node; `RollingUpdate` deadlocks.
`startupProbe` allows 15 min for the first boot (322 mods + world load).

### Boot safety (AGENTS.md "no startup remote-fetch")

`TYPE=NEOFORGE` makes the image run `mc-image-helper install-neoforge` on every
start, which on a host reboot fails before CoreDNS/Cilium are serving →
`CrashLoopBackOff`. This is the same class of bug as the paper-lobby reboot
incident. Mitigated by:

1. `NEOFORGE_INSTALLER` points at the installer **already on the PVC**, so
   nothing is downloaded.
2. `ForgeLikeInstaller.install()` loads the saved manifest and skips entirely
   when the MC + loader version match and the server entry still exists
   ("NeoForge version … is already installed").

After the one-time bootstrap the container needs **no** external network. The
egress policy exists only for that first install.

### Graceful shutdown

`terminationGracePeriodSeconds: 300` + a `preStop` hook running
`rcon-cli stop`. Without `ENABLE_RCON` the hook silently no-ops and the kubelet
SIGTERMs the JVM mid-save, which can corrupt region files on a 322-mod world.
RCON is not exposed by any Service, so the password stays pod-local.

## One-time bootstrap (data, not GitOps)

The server pack (503 MB) and world save (155 MB) are **not** in Git
(`.gitignore` excludes `world-data/`). Apply the manifests first so the PVC
exists, then stage the data into it.

```bash
# 1. let Argo create the PVC (Deployment will crash-loop until data lands)
kubectl -n argocd annotate application tenant-games-alpha \
  argocd.argoproj.io/refresh=hard --overwrite

# 2. stage the pack + world + installer into the PVC via a helper pod
#    (see "Staging" below)
```

### Staging

The PVC is `ReadWriteOnce` and the Deployment owns it, so scale the Deployment
to zero first, then mount the PVC in a throwaway pod:

```bash
kubectl -n prd-games-42wasd-admin scale deploy/atm10sky --replicas=0

cat <<'EOF' | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata: {name: atm10sky-staging, namespace: prd-games-42wasd-admin}
spec:
  restartPolicy: Never
  securityContext: {runAsUser: 10000, runAsGroup: 10000, fsGroup: 10000}
  containers:
    - name: stage
      image: alpine:3.20
      command: ["sh","-c","sleep 3600"]
      volumeMounts: [{name: data, mountPath: /data}]
  volumes:
    - name: data
      persistentVolumeClaim: {claimName: atm10sky-data}
EOF

# copy the archives in
kubectl -n prd-games-42wasd-admin cp ~/Downloads/ATM10SKY-2.2.0-server.zip \
  atm10sky-staging:/data/.bootstrap/server-pack.zip
kubectl -n prd-games-42wasd-admin cp ~/Downloads/world.zip \
  atm10sky-staging:/data/.bootstrap/world.zip

# unpack as uid 10000, and pre-seed the NeoForge installer
kubectl -n prd-games-42wasd-admin exec atm10sky-staging -- sh -c '
  cd /data
  apk add --no-cache unzip curl >/dev/null
  unzip -q .bootstrap/server-pack.zip -d /data
  mkdir -p /data/.bootstrap
  curl -fsSL -o /data/.bootstrap/neoforge-21.1.250-installer.jar \
    https://maven.neoforged.net/releases/net/neoforged/neoforge/21.1.250/neoforge-21.1.250-installer.jar
  # world must land as /data/world (LEVEL default)
  rm -rf /data/world
  unzip -q .bootstrap/world.zip -d /data
  chown -R 10000:10000 /data
  ls -la /data | head
'

kubectl -n prd-games-42wasd-admin delete pod atm10sky-staging
kubectl -n prd-games-42wasd-admin scale deploy/atm10sky --replicas=1
```

**Important:** the world must be extracted so that `level.dat` sits at
`/data/world/level.dat`. The provided `world.zip` already contains a top-level
`world/` directory, so `unzip -d /data` produces exactly that.

## Verify

```bash
kubectl -n prd-games-42wasd-admin get pods -l app=atm10sky -w
kubectl -n prd-games-42wasd-admin logs -f deploy/atm10sky | grep -E "Done|ERROR"
kubectl -n prd-games-42wasd-admin exec deploy/atm10sky -- id -u   # 10000
```

Expected: `Done (NNN.NNNs)! For help, type "help"`, and the port accepting
connections on the node at `192.168.8.240:30080`.

## Client requirement

Cracked/offline clients work (server `online-mode=false`), but the **client
must run the matching ATM10SKY 2.2.0 modpack** — 322 mods are not optional. Set
`ONLINE_MODE=FALSE` only; never enable `velocity` forwarding on this server.

## Follow-ups

- **World data is not backed up.** Same gap as the lobby. A CronJob doing
  `tar` of `/data/world` (or a PVC snapshot via the snapshot-controller already
  installed) would close it.
- Pack updates require re-staging: bump `NEOFORGE_VERSION` + `server-pack-file-id`
  in `maps/atm10sky-03a74e18/map.yaml` and repeat the bootstrap with the new
  archives. `ForgeLikeInstaller` will detect the version change and reinstall.
- `RCON_PASSWORD` is a plain value in Git. Acceptable only because no Service
  publishes `25575`; move it to a Secret if that changes.
