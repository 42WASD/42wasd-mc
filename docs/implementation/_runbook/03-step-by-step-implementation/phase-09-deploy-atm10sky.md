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
(`.gitignore` excludes `world-data/`). Let Argo create the PVC first, then stage
the data into it out of band.

### Why not a staging pod

A second pod **cannot** mount this volume. OpenEBS local-LVM is
`ReadWriteOnce` at the *mount* level here, not merely per-node — a staging pod
fails with:

```
MountVolume.SetUp failed ... rpc error: code = Internal
desc = verifyMount: device already mounted at [/var/lib/kubelet/pods/<uid>/...]
```

Scaling the Deployment to zero to free the volume also does not stick:
`platform-root` owns the Application and `selfHeal` reverts the replica count,
and patching `/spec/syncPolicy/automated` out of the Application is reverted for
the same reason.

**Therefore the correct approach is to stage directly through the host mount**
that the running pod already holds. This is a single-node cluster, so the path is
local:

```bash
# resolve the mount the atm10sky pod is holding
MNT=$(sudo mount | awk '/pvc-89104c77/{print $3}')
```

### Staging commands (what was actually run)

The Deployment is left crash-looping (it cannot boot without data); the crash
loop itself keeps the PVC mounted, which is exactly what we need.

```bash
MNT=/var/lib/kubelet/pods/<pod-uid>/volumes/kubernetes.io~csi/pvc-89104c77-.../mount

sudo cp ~/Downloads/ATM10SKY-2.2.0-server.zip "$MNT/.server-pack.zip"
sudo cp ~/Downloads/world.zip                    "$MNT/.world.zip"

# pack: config/ defaultconfigs/ kubejs/ mods/ (+ startserver.sh, user_jvm_args.txt)
sudo unzip -q -o "$MNT/.server-pack.zip" -d "$MNT"
# world: the archive already contains a top-level world/ dir -> /data/world
sudo unzip -q -o "$MNT/.world.zip" -d "$MNT"

# pre-seed the NeoForge installer so startup never touches the network
sudo mkdir -p "$MNT/.bootstrap"
sudo curl -fsSL -o "$MNT/.bootstrap/neoforge-21.1.250-installer.jar" \
  https://maven.neoforged.net/releases/net/neoforged/neoforge/21.1.250/neoforge-21.1.250-installer.jar

# the container runs as 10000; root-owned files would be unwritable
sudo chown -R 10000:10000 "$MNT"

# reclaim 1.5 GB — the archives are no longer needed
sudo rm -f "$MNT/.server-pack.zip" "$MNT/.world.zip"
```

Verify the layout before letting it boot:

```bash
sudo ls "$MNT"                      # config defaultconfigs kubejs mods world .bootstrap
sudo ls "$MNT/world/level.dat"      # must exist
sudo du -sh "$MNT"/{mods,world}     # 603M, 644M
```

The crash loop then recovers on its next back-off expiry — no further action
needed.

### Observed result

```
[22:44:04] [Server thread/INFO] [minecraft/DedicatedServer]: Preparing level "world"
[22:44:05] [Server thread/INFO] [minecraft/DedicatedServer]: Done (1.706s)! For help, type "help"
[22:44:05] [Server thread/INFO] [minecraft/RconThread]: RCON running on 0.0.0.0:25575
```

`install-neoforge` did **not** run: the pre-seeded installer plus the matching
loader version made `ForgeLikeInstaller` skip it, so startup consumed no
external network.

Verification:

```
$ kubectl -n prd-games-42wasd-admin exec deploy/atm10sky -- id -u
10000
$ ... grep -E '^(online-mode|level-type|allow-flight|max-tick-time|enable-rcon)' /data/server.properties
allow-flight=true
enable-rcon=true
level-type=skyblockbuilder\:skyblock
max-tick-time=180000
online-mode=false
$ ... ls /data/mods/*.jar | wc -l
322
$ timeout 5 bash -c 'cat < /dev/null > /dev/tcp/192.168.8.240/30080'
PORT 30080 OPEN
```

Note `6` restarts on the pod: those are all from the pre-staging crash loop
(`install-neoforge` failing / no `libraries/`), not post-boot failures. The
container has been stable since data landed.

## Client requirement

Minecraft **1.21.1** + **NeoForge 21.1.250**, running the **All the Mods 10: To
the Sky** pack v**2.2.0** (CurseForge slug `all-the-mods-10-sky`, project ID
**1298402**, server pack file ID **9262010**). 322 mods are not optional.

This is the **"To the Sky"** pack, not base "All the Mods 10" — a different
pack that will not connect. Skyblock-identifying mods confirmed on disk:
`SkyblockBuilder-21.1.37`, `cobblegengalore`.

Connection: `mc-oompas.42base.com` — **no port needed** (mc-router dispatches on
the handshake hostname; see `phase-10-add-mc-router.md`). Never enable
`velocity` forwarding on this server.

### ⚠️ Offline / cracked clients are currently BLOCKED

An earlier version of this section claimed cracked clients work because
`online-mode=false`. **That was wrong.** The live properties are:

```text
online-mode=false
enforce-secure-profile=true
```

`enforce-secure-profile=true` requires a **cryptographically signed profile key**
that only a genuine Microsoft-authenticated session can produce. With
`online-mode=false` there is no such key, so offline clients are rejected at
login. A legitimately-owned account works fine.

### Turning off `enforce-secure-profile` (when you want offline clients)

**The trap:** this server sets `OVERRIDE_SERVER_PROPERTIES=false`, so the image
applies env-var-derived properties **only on a fresh `/data`**. After that
`server.properties` on the PVC is authoritative. Adding
`ENFORCE_SECURE_PROFILE` to the Deployment and resyncing Argo will therefore
**change nothing** — the pod restarts and keeps the old value.

The image *does* support the variable (it is in
`/image/property-definitions.json` as `"enforce-secure-profile": {"env":
"ENFORCE_SECURE_PROFILE"}`), but `OVERRIDE_SERVER_PROPERTIES=false` gates it
out. Two changes are needed, in this order.

**1. Edit the property on the PVC, then restart the server.**

The volume is `ReadWriteOnce` and OpenEBS local-LVM allows exactly **one
mount**, so do not scale to zero first: with no pod running there is no mount
point and the host path does not exist. Edit in place while the pod is up
(the JVM reads `server.properties` once at boot, so the edit only takes effect
on the next start), then stop the server cleanly.

```bash
NS=prd-games-42wasd-admin

# Resolve the host-side mount. Note it is keyed on the PVC *UID*
# (pvc-<uid>), NOT on the PVC name — searching for "atm10sky-data" finds
# nothing, because local-LVM directories are named by UID.
PVC_UID=$(kubectl -n $NS get pvc atm10sky-data -o jsonpath='{.metadata.uid}')
MOUNT=$(sudo find /var/lib/kubelet/pods -maxdepth 6 -type d \
          -path "*pvc-$PVC_UID/mount" 2>/dev/null | head -1)
echo "$MOUNT"
# expected shape:
#   /var/lib/kubelet/pods/<pod-uid>/volumes/kubernetes.io~csi/pvc-<uid>/mount

# Flip the property on the live mount
sudo sed -i 's/^enforce-secure-profile=.*/enforce-secure-profile=false/' \
  "$MOUNT/server.properties"
sudo grep -E '^(online-mode|enforce-secure-profile)' "$MOUNT/server.properties"
```

Then restart so the JVM re-reads it. `rcon-cli stop` is the clean path — a
SIGKILL risks a half-written world across 322 mods.

```bash
POD=$(kubectl -n $NS get pod -l app=atm10sky -o jsonpath='{.items[0].metadata.name}')
kubectl -n $NS exec "$POD" -- rcon-cli stop
```

`restartPolicy: Always` brings the container straight back, and the image
finds `/data` already populated, so `OVERRIDE_SERVER_PROPERTIES=false` leaves
your edited file alone.

> **If `$MOUNT` is empty:** no pod is running, so the volume is unmounted. Scale
> up first (`kubectl -n $NS scale deploy atm10sky --replicas=1`), wait for
> `Running`, then re-run the block above.

**2. Make it survive a re-bootstrap.** While you are there, add the variable to
the Deployment so a *fresh* `/data` gets the same value:

```yaml
- name: ENFORCE_SECURE_PROFILE
  value: "false"
```

Without step 1 it does nothing; without step 2 a rebuilt volume silently
reverts to `true`. Do both.

**3. Verify from a client.** The status ping always answers (it has no login
stage), so a ping is **not** proof. You need an actual login attempt from an
offline client; a rejection reads roughly:

```text
Failed to verify username! / Invalid session
```

Also mirror the change on `paper-lobby` (`clusters/alpha/lobby/paper.yaml`),
which has the same `online-mode=false` + `enforce-secure-profile=true` pair and
therefore the same restriction behind Velocity.

> Prefer to keep it `true`? That is the safer default: it stops username
> spoofing, and with no auth gate on this network
> (see the reference design's "in-game auth gate") an offline client can claim
> any username it likes. Turning it off is a deliberate, reversible choice, not
> a fix.

## Follow-ups

- **World data is not backed up.** Same gap as the lobby. A CronJob doing
  `tar` of `/data/world` (or a PVC snapshot via the snapshot-controller already
  installed) would close it.
- Pack updates require re-staging: bump `NEOFORGE_VERSION` + `server-pack-file-id`
  in `maps/atm10sky-03a74e18/map.yaml` and repeat the bootstrap with the new
  archives. `ForgeLikeInstaller` will detect the version change and reinstall.
- `RCON_PASSWORD` is a plain value in Git. Acceptable only because no Service
  publishes `25575`; move it to a Secret if that changes.
