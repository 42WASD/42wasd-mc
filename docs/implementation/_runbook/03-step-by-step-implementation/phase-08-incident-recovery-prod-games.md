---
phase: 03-step-by-step-implementation/rollout-order
---

# Runbook — Incident: prod-games pods crashing after reboot

After a host reboot, every workload in `prd-games-42wasd-admin` was crashing:
`velocity` (2×) and `paper-lobby` in `CrashLoopBackOff`, `nakama` (2×) stuck in
`Unknown`. Root cause was **not** a manifest bug and **not** the networkpolicy
YAML — it was **stale CiliumEndpoint (CEP) data carrying the old DHCP node IP
`192.168.8.132`** after the node had been pinned to static `192.168.8.240`.
The namespaces ended healthy (`cockroachdb`, `velocity`×2, `paper-lobby`,
`nakama`×2 all `1/1 Running`).

## Root cause

After the node IP was changed from the DHCP lease (`.132`) to the pinned static
IP (`.240`), the persisted **`CiliumEndpoint` CRs still stored
`status.networking.node: 192.168.8.132`**, while Cilium ran at `192.168.8.240`.
Cilium's endpoint synchronizer refused to take ownership of these "not local"
CEPs:

```
error="endpoint sync cannot take ownership of CEP that is not local:
CEP's pod \"...\", pod's hostIP \"192.168.8.132\", cilium nodeIP \"192.168.8.240\")"
```

Because Cilium would not program the datapath for those endpoints, **pod-to-pod
and pod-to-DNS traffic broke**, which cascaded:

- `velocity` / `paper-lobby` → could not resolve `fill.papermc.io` via CoreDNS
  (they download the server jar on first start) → `CrashLoopBackOff`.
- `nakama` → could not reach CockroachDB (`10.43.45.225:26257` connect timeout)
  → crash.

DNS itself was confirmed broken *inside* the namespace (a PSS-compliant
`busybox` probe got `connection timed out; no servers could be reached` for
`nslookup ... 10.43.0.10`), while the same probe in the `default` namespace
resolved fine — pointing squarely at the CNI dataplane, not at the apps.

## What was done

### 1. Diagnose

- `kubectl get pods -n prd-games-42wasd-admin -o wide` → crash/unknown pods.
- `kubectl logs` on the crashing pods → DNS `DnsNameResolverTimeoutException`
  (`velocity`, `paper-lobby`) and `dial tcp ...26257 connection timed out`
  (`nakama`).
- Probes: `nslookup fill.papermc.io 10.43.0.10` inside the namespace failed,
  outside succeeded.
- `kubectl -n kube-system logs ds/cilium` → the endpoint-ownership warnings
  against `.132`.

### 2. Fix the stale Cilium endpoints

- Confirmed pod `hostIP=192.168.8.240` while CEP `node=192.168.8.132`.
- Counted `38` stale CEPs (of 43) carrying `.132`; only 5 already `.240`.
- Deleted the stale CEPs so Cilium would regenerate them.
- **Restarted the Cilium agent** so it re-discovered all local endpoints and
  rewrote every CEP with the correct node IP (deleting CEPs alone only
  regenerated a few — the in-memory node identity needed a restart):

```bash
export KUBECONFIG=/etc/rancher/rke2/rke2.yaml
# count CEPs by node
kubectl get cep -A -o json | python3 -c 'import sys,json;from collections import Counter;
d=json.load(sys.stdin);print(Counter(i["status"]["networking"]["node"] for i in d["items"]))'
# delete all stale CEPs (node == old DHCP IP)
kubectl delete cep -A -l ...  # per-CEP delete for the 38 stale ones
# restart the agent so it regenerates everything with the correct node
kubectl -n kube-system rollout restart daemonset cilium
kubectl -n kube-system rollout status ds/cilium --timeout=180s
```

After restart: `CEP count=43`, `{'192.168.8.240': 43}`, `sync errors=0`.

### 3. Recreate the game pods now that networking is healthy

The deployment definitions were already correct; the old pods had been
crash-looping for ~40 h with stale CEPs. After the Cilium fix, `paper-lobby`
recovered by itself. For `velocity` and `nakama`, deleted the stale pods so the
Deployment recreated them fresh:

```bash
kubectl -n prd-games-42wasd-admin delete pod -l app=velocity
kubectl -n prd-games-42wasd-admin delete pod -l app=nakama
```

`velocity` and `paper-lobby` then came up `1/1 Running` immediately.

### 4. Add the missing one-way ingress NetworkPolicy for Nakama → CockroachDB

`nakama`'s init container (`nakama-migrate`) then hit a **second, separate**
issue: it could not reach CockroachDB on `26257`. The namespace is
`default-deny` on **both ingress and egress**. `allow-games-egress` grants
nakama egress → cockroachdb, but Kubernetes NetworkPolicies are **one-way** —
the DB pod also needs an **ingress** allow from nakama. This was the same
pattern as the existing `allow-proxy-to-paper-lobby` (velocity → paper).

Added `allow-nakama-to-cockroachdb` (in `clusters/alpha/networkpolicy.yaml`):

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-nakama-to-cockroachdb
  namespace: prd-games-42wasd-admin
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/name: cockroachdb
  policyTypes:
    - Ingress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: nakama
      ports:
        - protocol: TCP
          port: 26257
```

Applied and restarted nakama. The init container connected to
`CockroachDB CCL v26.2.5`, applied migrations, and both nakama pods came up
`1/1 Running`.

## End state

```
cockroachdb-0    1/1  Running
nakama           1/1  Running  (×2)
paper-lobby      1/1  Running
velocity         1/1  Running  (×2)
```

All CiliumEndpoints carry `node: 192.168.8.240`; no endpoint-ownership errors.

## Lessons / follow-ups

- After any change of a node's IP, **restart the Cilium agent** (or delete
  stale CEPs **and** restart) so all `CiliumEndpoint` CRs are rewritten with the
  current node IP. Deleting CEPs alone is insufficient — the in-memory node
  identity must re-discover endpoints.
- `default-deny` on ingress **and** egress means every intra-namespace flow
  needs a matching ingress allow on the destination, not just an egress allow
  on the source.
- DNS timeouts in a namespace are a strong hint the CNI dataplane is broken for
  those pods, not that CoreDNS is down — verify by comparing a probe in the
  affected namespace vs the `default` namespace.

## Follow-up: the games namespace is now Argo CD-managed (GitOps)

After this incident, the whole `clusters/alpha` overlay (netpols + all game
workloads) was wired into Argo CD so the exact network state is declared in
Git and re-converged automatically — no more manual `kubectl apply` of
networkpolicies.

- Argo app **`tenant-games-alpha`** (defined in the **iac** repo at
  `infra/kubernetes/bootstrap/argocd/apps/tenant-games-alpha.yaml`) points at
  this repo's `clusters/alpha` path, destination
  `prd-games-42wasd-admin`, with `ServerSideApply` + `selfHeal` + `prune`.
- The `prd-games-42wasd-admin` **Namespace** is owned by the iac
  `platform-namespaces` app, so it is NOT declared in this repo's
  `clusters/alpha/kustomization.yaml` (two Argo apps must not own the same
  resource).
- **CockroachDB was migrated from Helm to plain manifests** so Argo owns it:
  the bogus `CrdbCluster` (operator CR) was replaced with the real running
  StatefulSet + its headless/public Services + the cert-rotation CronJobs.
  The TLS cert secrets (`cockroachdb-node-secret`,
  `cockroachdb-client-secret`) are regenerated by the self-signer CronJobs and
  are **not** committed.

If game workloads or netpols drift again, check that the `tenant-games-alpha`
Argo app is `Synced`/`Healthy` first, then the Git state under
`clusters/alpha/` — that is now the single source of truth.

---

# Incident 2 — recurring "bad IO" crash loops were ext4 UID quota (2026-11-06)

## Symptom

Game pods crash-looped at irregular intervals — `velocity`, `paper-lobby`,
`cockroachdb` — with errors that looked like storage/hardware failure:

```
[mc-image-helper] ERROR : 'install-paper' command failed
Caused by: java.io.IOException: Disk quota exceeded
```

```
ERROR: cannot load certificates.
validating node cert: empty certificate file: node.crt
```

A **reboot always appeared to fix it**, which is what made it look like flaky
IO or a boot-order race.

## Root cause

Not hardware. Three facts combine:

1. `/` is mounted **ext4 with `quota,usrquota`**:

   ```
   $ findmnt -no SOURCE,FSTYPE,OPTIONS /
   /dev/mapper/ubuntu--vg-ubuntu--lv ext4 rw,relatime,quota,usrquota
   ```

2. **`emptyDir` volumes live on `/`.** `/var/lib/kubelet` is on the same
   device as `/` (the 320 GB `xfs` at `/var/lib/rancher/rke2` is a *different*
   mount with `noquota`):

   ```
   $ findmnt -T /var/lib/kubelet/pods/<uid>/volumes/kubernetes.io~empty-dir/data
   /dev/mapper/ubuntu--vg-ubuntu--lv  /
   ```

3. **Every workload ran as `runAsUser: 1000` — the human login `jyao`.**

So all ephemeral writes by all game pods were charged to a *person's* home
quota (soft 10 GiB, hard 15 GiB). `EDQUOT` is the kernel refusing the write —
it reads like an IO error but is purely the quota subsystem.

Verify:

```bash
sudo repquota -u /        # '+' = over soft limit, '*' = grace expired
sudo quota -u jyao -s
sudo find / -xdev -uid 1000 -type f -printf '%b\n' \
  | awk '{s+=$1} END {printf "%.2f GB\n", s*512/1024/1024/1024}'
```

Evidence that it is **not** hardware:

```bash
sudo dmesg -T | grep -Ei 'i/o error|blk_update_request|nvme.*(error|timeout|reset)|EXT4-fs error'
# → no output
sudo smartctl -H /dev/nvme2n1     # → PASSED (same for nvme0n1, nvme1n1)
```

### Why a reboot "fixed" it

Restarting pods **wipes their `emptyDir`**. Prometheus alone was holding
~3.2 GiB of TSDB on an `emptyDir`, all charged to UID 1000. A reboot recreated
that pod, deleted the data, and freed the quota under the same UID — so the
next failure was days away. Nothing was actually repaired.

Note: the 2026-11-06 crash was **not** reboot-related — the host had been up
10h44m when velocity failed at 20:02. Correlation, not cause.

## Fix

Moved all workloads to a **dedicated, non-human UID/GID 10000**.

### 1. Migrate PVC ownership FIRST

The PVC data was owned by `1000:1000`. Changing the UID without migrating
would lock the servers out of their own world data. Back up ownership, then
chown:

```bash
sudo mkdir -p /var/backups/uid-migration-2026-11-06
sudo find "$PAPER" -printf '%U:%G %m %p\n' | sort -k3 \
  | sudo tee /var/backups/uid-migration-2026-11-06/paper-lobby.owners.txt >/dev/null
sudo find "$CRDB"  -printf '%U:%G %m %p\n' | sort -k3 \
  | sudo tee /var/backups/uid-migration-2026-11-06/cockroachdb.owners.txt >/dev/null

sudo chown -R 10000:10000 "$PAPER"
sudo chown -R 10000:10000 "$CRDB"
```

(23,605 paths backed up: 17,931 paper-lobby + 5,674 cockroachdb.)

### 2. Manifests (`clusters/alpha/`, applied by Argo `tenant-games-alpha`)

- `runAsUser`/`runAsGroup`/`fsGroup` → `10000` for paper-lobby, velocity,
  nakama, cockroachdb, and both cert-rotation CronJobs.
- itzg `PUID`/`PGID` → `"10000"`, so the image does not re-chown `/data` back
  to the old uid on startup.
- `emptyDir.sizeLimit: 2Gi` on velocity and nakama `data` volumes — an
  explicit cap so they can never silently consume node-local disk.

UID 10000 is still PodSecurity `restricted` compliant (that profile only
requires *non-root*, not a specific uid). Verified nothing on the host uses
10000:

```bash
getent passwd 10000     # no account
sudo find / -xdev -uid 10000 -maxdepth 4   # nothing
```

### 3. Prometheus / Alertmanager (operator-managed, not GitOps)

These were the largest quota consumers and are **not** in Argo. Patched the
CRs directly:

```bash
kubectl -n monitoring patch prometheus prometheus-kube-prometheus-prometheus \
  --type=merge -p '{"spec":{
    "retention":"10d","retentionSize":"2GiB",
    "securityContext":{"runAsNonRoot":true,"runAsUser":10000,
      "runAsGroup":10000,"fsGroup":10000,
      "seccompProfile":{"type":"RuntimeDefault"}},
    "storage":{"emptyDir":{"sizeLimit":"3Gi"}}}}'

kubectl -n monitoring patch alertmanager prometheus-kube-prometheus-alertmanager \
  --type=merge -p '{"spec":{
    "securityContext":{"runAsNonRoot":true,"runAsUser":10000,
      "runAsGroup":10000,"fsGroup":10000,
      "seccompProfile":{"type":"RuntimeDefault"}},
    "storage":{"emptyDir":{"sizeLimit":"1Gi"}}}}'
```

`retentionSize: 2GiB` is the important one: it is the **only** mechanism here
that *rotates* (deletes oldest TSDB blocks) rather than just failing the write.
It sits below the 3Gi volume cap so Prometheus reclaims space before the
filesystem fills.

### 4. Apply

```bash
git -C 42wasd-mc push origin main          # 234bf71
kubectl -n argocd annotate application tenant-games-alpha \
  argocd.argoproj.io/refresh=hard --overwrite
# OrderedReady blocked on the crash-looping pod; delete it to force recreation:
kubectl -n prd-games-42wasd-admin delete pod cockroachdb-0
```

## Verified (live)

```
cockroachdb-0                 1/1 Running
nakama ×2                     1/1 Running
paper-lobby                   1/1 Running
velocity ×2                   1/1 Running

$ kubectl exec … -- id -u      # all six containers
10000 (×6)
```

Write access on the migrated PVCs, as 10000:

```
/data                        WRITE OK
/cockroach/cockroach-data    WRITE OK
```

Quota reclaimed from **8,253,400 → 4,969,348 blocks** (~3.2 GiB freed) purely
by moving Prometheus off UID 1000:

```
$ sudo quota -u jyao
  blocks 4,969,348   soft 10,485,760   hard 15,728,640
```

## Residual risk / follow-ups

- `usrquota` is still on `/`. Workloads are now immune, but a human filling
  their own home can still exhaust the *filesystem* itself. Consider moving
  kubelet's `root-dir` off `/` during a maintenance window (requires draining
  the node), or dropping `usrquota` from `/`.
- Still running as UID 1000: `rke2-metrics-server`, `rke2-snapshot-controller`
  (kube-system), `dex` (security). Low traffic, but they share the same bucket.
- `jyao-42admin` (UID 1001) is over its soft quota with grace expired — latent,
  nothing currently runs as that uid. Clear it with `edquota -t` /
  `setquota`.
- Prometheus/Alertmanager CR patches are **not** GitOps-managed. If the
  `prometheus` Helm release is ever `helm upgrade`d with values that touch
  `spec.storage`/`securityContext`, re-apply them — or move the monitoring CRs
  into Argo.

## Lesson

"Disk quota exceeded" is a quota signal, not an IO signal. When a crash loop
disappears on reboot, ask **what a reboot frees** — here it was `emptyDir`
contents. Always check `findmnt` for `quota` flags on the filesystem backing
`/var/lib/kubelet` before blaming hardware, and never run workloads as a UID
that belongs to a human account.