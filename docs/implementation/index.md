# Implementation — Progress

This page tracks the build status of every phase in the
[Build (Implementation Phases)](../reference-design/03-step-by-step-implementation/index.md)
section of the Reference Design.

> The phase-by-phase **rollout order** is defined in
> [Phase 30 — Rollout order](../reference-design/03-step-by-step-implementation/rollout-order/index.md).

## How to update

- Edit `docs/implementation/progress.yaml` to bump a phase's status
  (`done`, `in-progress`, `not-started`, `blocked`, `deferred`).
- Regenerate this page:
  `python3 scripts/docs/docs-generate-implementation.py`
- Rebuild:
  `cd projects && uv run mkdocs build --strict -f ../mkdocs.yml`

<!-- BEGIN_GENERATED_IMPLEMENTATION -->

## Overall progress

**6 / 31** phases/sections complete (**19%**).

<div class="progress-row" style="max-width:720px;padding:8px 0;"><div class="progress-track"><div class="progress-fill progress-fill--shimmer" style="--w:19.4%"></div></div><div class="progress-pct">19%</div></div>

| Status | Count |
|--------|-------|
| ✅ done | 6 |
| 🔶 in-progress | 0 |
| ⬜ not-started | 25 |
| ❌ blocked | 0 |
| ⏸️ deferred | 0 |

## Progress by part

### 19% — Part III — Step-by-step implementation

<div class="tip" style="display:flex;align-items:center;gap:8px;max-width:520px;padding:2px 0 10px;"><div class="progress-track"><div class="progress-fill" style="--w:19.0%"></div></div><div class="progress-pct" style="font-size:.85em;">19%</div><div class="tip-box"><strong>Done (6)</strong>
• Decide names before deploying
• Create repository structure
• Create Kubernetes namespaces
• Install OpenKruiseGame
• Install KEDA and the observability stack
• Deploy CockroachDB and Nakama
<hr style="opacity:.3;margin:6px 0;"><strong>Pending (25)</strong>
• Deploy Velocity
• Deploy the Paper lobby
• Install TAB
• Add ViaVersion and ViaBackwards
• Deploy the Forge 1.20.1 fantasy runtime
• Define the runtime catalog
• Define map metadata
• Build the World Controller
• Build NetworkBridge for Velocity
• Implement friends and parties
• Implement `/join <friend>`
• Implement pending cross-runtime invites
• Publish Modrinth Server Projects
• Add packwiz CI
• Add exact world/dimension TAB information
• Implement the glitch/random portal
• Add mc-router
• Add idle sleep
• Add Agones only for session worlds
• Add AI proximity chat
• Add object storage for the community upload pipeline
• Community map upload pipeline
• Backups
• Monitoring
• Rollout order</div></div>

- ✅ `done` — [Phase 0 — Decide names before deploying](../reference-design/03-step-by-step-implementation/decide-names-before-deploying/index.md)

<details markdown="1" class="runbook">
<summary>✅ 📜 Build log — Decide names before deploying</summary>

# Runbook — Phase 0: Decide names before deploying

## What was done

Locked the stable identifiers for the deployment, per
`docs/reference-design/03-step-by-step-implementation/decide-names-before-deploying/index.md`.

- Confirmed the cluster/context and namespace from the live cluster:
  - Context: `alpha-games-prd`
  - Namespace: `prd-games-42wasd-admin` (dev mirror: `dev-games-42wasd-admin`)
- Confirmed the public hostname: `minecraft.42base.com` (Cloudflare).
- Defined the world logical ID scheme: `<map-slug>-<uuid8>` (8-hex UUID
  prefix) to guarantee non-collision without a registry/counter.
- Updated the phase-0 reference-design doc with the recorded identifiers.

## Commands run

```bash
# Verify context and namespaces (read-only probes)
kubectl config current-context
kubectl config view --minify -o jsonpath='{.contexts[0].context.namespace}'
kubectl get ns

# No cluster mutations performed in this phase.
```

## Verified / observed

- Namespaces `prd-games-42wasd-admin` and `dev-games-42wasd-admin` exist on
  the cluster; no `platform`/`proxy`/`game-backends` namespaces exist (those
  live only in stale `infra/` manifests).
- Context namespace resolves to `prd-games-42wasd-admin`.
- Marked phase 0 `done` in `progress.yaml` and regenerated
  `docs/implementation/index.md`.
- **Fixed a generator bug** in `scripts/docs/docs-generate-implementation.py`:
  `load_progress()` returned the nested `progress.yaml` dict, but `status_of()`
  looks status up by flat slash-paths, so statuses were never read (all phases
  always showed `not-started`). Added `_flatten()` to collapse nested status
  keys into slash-paths. After the fix, phase 0 correctly shows `✅ done`
  (1/31).
- Ignored large world data in `.gitignore` (`world-data/`, `world-data-export-*.tar.gz`).

## Outcome

Phase 0 is a documentation-only decision phase. Next: Phase 1 — Create
repository structure, then Phase 2 — create the namespaces (aligning the
`infra/` manifests to the actual `prd-games-42wasd-admin` namespace).

</details>

- ✅ `done` — [Phase 1 — Create repository structure](../reference-design/03-step-by-step-implementation/create-repository-structure/index.md)

<details markdown="1" class="runbook">
<summary>✅ 📜 Build log — Create repository structure</summary>

# Runbook — Phase 1: Create repository structure

## What was done

Established the top-level repository structure that matches the reference
design exactly, and migrated the stale in-place Kubernetes manifests into it.

- Created top-level directories: `clusters/`, `runtimes/`, `maps/`,
  `services/`, each with a `README.md` explaining its role.
- Created `clusters/alpha/` (alpha-games-prd) with the component layout
  (`velocity/`, `lobby/`, `nakama/`, `cockroachdb/`, `mc-router/`,
  `monitoring/`) per the Phase 1 reference-design doc.
- Migrated the old `infra/kubernetes/{platform,tenants}` manifests into
  `clusters/alpha/<component>/` and reconciled every namespace reference from
  the stale `platform`/`proxy`/`game-backends` values to the real games
  namespace `prd-games-42wasd-admin`.
- Removed the `infra/` directory entirely (it is not part of the reference
  design's target structure). Its secret/kubeconfig ignore rules were folded
  into the root `.gitignore`; the operator architecture notes were already
  covered by `docs/reference-design/` and `docs/guides/`.
- Updated root `README.md` and `docs/index.md` to describe the new layout.
- Added kustomize bases for each component and an aggregate overlay at
  `clusters/alpha/kustomization.yaml`.

## Commands run

```bash
# Create the top-level structure
mkdir -p clusters/alpha/{velocity,lobby,nakama,cockroachdb,mc-router,monitoring}
mkdir -p runtimes maps services

# Remove the stale infra/ tree (fully migrated + folded ignore rules)
rm -rf infra

# Validate the alpha overlay renders cleanly and targets the right namespace
kubectl kustomize clusters/alpha >/dev/null
kubectl kustomize clusters/alpha | grep -E "kind:|name: prd-games|namespace:"
```

## Verified / observed

- `kubectl kustomize clusters/alpha` builds cleanly.
- All rendered resources target namespace `prd-games-42wasd-admin`.
- No remaining references to the old `platform`/`proxy`/`game-backends`
  namespaces in the migrated manifests.
- Marked phase 1 `done` in `progress.yaml` and regenerated
  `docs/implementation/index.md`.

</details>

- ✅ `done` — [Phase 2 — Create Kubernetes namespaces](../reference-design/03-step-by-step-implementation/create-kubernetes-namespaces/index.md)

<details markdown="1" class="runbook">
<summary>✅ 📜 Build log — Create Kubernetes namespaces</summary>

# Runbook — Phase 2: Create Kubernetes namespaces

## What was done

Reconciled the namespace strategy with the tenant-namespace policy that
actually exists on `alpha-games-prd`, rather than creating the reference
design's generic `minecraft` / `minecraft-system` split.

- **Confirmed the live cluster state** (context `alpha-games-prd`):
  `prd-games-42wasd-admin` already exists and is `Active`; its `dev-`
  mirror `dev-games-42wasd-admin` also exists. No `minecraft`,
  `minecraft-system`, `platform`, `proxy`, or `game-backends` namespaces
  exist.
- **Decision: one shared games namespace**, not the two-namespace split.
  Grounded in Kubernetes namespace guidance (namespaces are for
  team/tenant/resource boundaries; prefer labels within a shared namespace
  unless hard isolation is needed) and Argo CD ApplicationSets (host many
  games in one namespace, label-scoped).
- **Documented the "why"** in the Phase-2 reference-design doc:
  env boundary = namespace (`prd-` vs `dev-`); shared platform (Velocity,
  lobby, World Controller, NetworkBridge, CockroachDB, Nakama) must not be
  per-game; game/world boundary = labels + Argo CD `Application`s.
- Kept the declarative source of truth at
  `clusters/alpha/namespace.yaml` (namespace `prd-games-42wasd-admin`,
  labels `environment: prd` + `app.kubernetes.io/managed-by: gitops`).

## Commands run

```bash
# Read-only probes — confirm existing namespaces and context
kubectl config current-context
kubectl get ns

# No mutation: the namespace already exists on the cluster.
# Declarative manifest is the GitOps source of truth; apply only if a
# fresh cluster lacks it:
# kubectl apply -f clusters/alpha/namespace.yaml
```

## Verified / observed

- Context is `alpha-games-prd`.
- `prd-games-42wasd-admin` present (Active) — no `kubectl apply` needed for
  the existing prod namespace.
- All component manifests now target `prd-games-42wasd-admin` (reconciled in
  Phase 1) — grep found no stale `platform`/`proxy`/`game-backends` refs.
- Marked phase 2 `done` in `progress.yaml` and regenerated
  `docs/implementation/index.md`.

## Outcome

Namespace strategy is locked as **single shared games namespace + labels +
per-game Argo CD Applications**. Next: Phase 3 — Install OpenKruiseGame.

</details>

- ✅ `done` — [Phase 3 — Install OpenKruiseGame](../reference-design/03-step-by-step-implementation/install-openkruisegame/index.md)

<details markdown="1" class="runbook">
<summary>✅ 📜 Build log — Install OpenKruiseGame</summary>

# Runbook — Phase 3: Install OpenKruiseGame

## What was done

Installed the two OpenKruise components the World Controller depends on —
**Kruise** (core controllers) and **Kruise-Game** (GameServer/GameServerSet) —
into `alpha-games-prd`. Installed as `jyao` (cluster admin) via an interactive
`ssh jyao@alpha` session.

- **Helm** was not present on the host, so installed
  `helm` v3.16.4 to `~/bin/helm` (home bin, no sudo needed).
- **Kruise** core `1.9.1` → namespace `kruise-system`, helm release `kruise`.
- **Kruise-Game** `1.1.0` (the pinned OKG version from
  `verified-versions.yaml`) → namespace `kruise-game-system`, helm release
  `kruise-game`.

### Install note (helm + local tgz quirk)

Helm's `--create-namespace` does **not** work when installing from a local
`.tgz` path. The namespace must be created and **owned by Helm** first, or helm
fails with `cannot re-use a name that is still in use` / invalid ownership.
Reliable recipe:

```bash
kubectl create namespace kruise-system
kubectl label namespace kruise-system app.kubernetes.io/managed-by=Helm
kubectl annotate namespace kruise-system \
  meta.helm.sh/release-name=kruise \
  meta.helm.sh/release-namespace=kruise-system
helm install kruise /tmp/kruise.tgz --namespace kruise-system
```

A corrupted failed release was purged by deleting the namespace; the
`kruise-daemon-config` namespace left by the daemon was removed too.

## Commands run

```bash
# On host (jyao@alpha): install helm to home bin
curl -fsSL https://get.helm.sh/helm-v3.16.4-linux-amd64.tar.gz -o /tmp/helm.tgz
tar -xzf /tmp/helm.tgz -C /tmp && mv /tmp/linux-amd64/helm ~/bin/helm

# Download charts (GitHub CDN refused once transiently; retry succeeded)
curl -fsSL -o /tmp/kruise.tgz \
  https://github.com/openkruise/charts/releases/download/kruise-1.9.1/kruise-1.9.1.tgz
curl -fsSL -o /tmp/kruise-game.tgz \
  https://github.com/openkruise/charts/releases/download/kruise-game-1.1.0/kruise-game-1.1.0.tgz

# Kruise core
kubectl create namespace kruise-system
kubectl label namespace kruise-system app.kubernetes.io/managed-by=Helm
kubectl annotate namespace kruise-system \
  meta.helm.sh/release-name=kruise meta.helm.sh/release-namespace=kruise-system
helm install kruise /tmp/kruise.tgz --namespace kruise-system

# Kruise-Game
kubectl create namespace kruise-game-system
kubectl label namespace kruise-game-system app.kubernetes.io/managed-by=Helm
kubectl annotate namespace kruise-game-system \
  meta.helm.sh/release-name=kruise-game meta.helm.sh/release-namespace=kruise-game-system
helm install kruise-game /tmp/kruise-game.tgz --namespace kruise-game-system

# Verify CRDs + smoke test the 0→1 primitive
kubectl api-resources --api-group=game.kruise.io
kubectl apply -f /tmp/gss-smoke.yaml   # GameServerSet replicas: 1
kubectl get gs -n default              # smoke-gss-0 -> Ready
kubectl delete gameserverset smoke-gss -n default
```

## Verified / observed

- Helm releases `kruise` (deployed) and `kruise-game` (deployed).
- Kruise controller-manager 2/2 Ready + daemon Running in `kruise-system`.
- Kruise-Game controller-manager Running in `kruise-game-system`.
- CRDs present: `gameservers.game.kruise.io`, `gameserversets.game.kruise.io`
  (plus full `apps.kruise.io` / `policy.kruise.io` set from Kruise core).
- **Acceptance passed:** scratch `GameServerSet smoke-gss` with `replicas: 1`
  produced `GameServer smoke-gss-0` in `Ready` state with a Running pod
  (readiness gates 2/2), then cleaned up. This is the exact primitive the
  World Controller drives.
- Added `kruise: 1.9.1` and `openkruisegame: 1.1.0` to
  `verified-versions.yaml`.
- Marked phase 3 `done` in `progress.yaml` and regenerated
  `docs/implementation/index.md`.

## Post-audit correction (2026-08-24) — kruise-daemon socket path on RKE2

A phase 0-5 audit found `kruise-daemon` was CrashLoopBackOff-ing on the live
alpha cluster, even though the helm release reported `deployed`.

### The blocker

- **Symptom:** `kubectl get pods -n kruise-system -l app=kruise-daemon` showed
  `0/1 CrashLoopBackOff` (~21 restarts). The daemon log repeated:
  `Failed to new daemon: failed to new runtime factory: not found container
  runtime sock`.
- **Root cause (proven):** RKE2 runs containerd with a **non-standard socket
  path** — `/run/k3s/containerd/containerd.sock`. The OpenKruise `kruise`
  chart defaults `daemon.socketLocation` to `/var/run`, so the
  kruise-daemon looked for the runtime socket in the wrong place and never
  found it. This is the documented K3s/RKE2 case in the OpenKruise install
  docs: "Usually K3s has a different runtime path from the default `/var/run`.
  You have to set `daemon.socketLocation` to the real runtime socket path."
- **Fix:** reinstall the `kruise` release with the RKE2 socket location
  (`/run/k3s`, where the default socket file name `containerd.sock` lives):

  ```bash
  helm upgrade kruise openkruise/kruise -n kruise-system \
    --reuse-values --set daemon.socketLocation=/run/k3s
  ```

### Verified after correction

- `kubectl get ds kruise-daemon -n kruise-system` → `1/1` READY (was `0/1`).
- Daemon pod `kruise-daemon-*` → `1/1 Running`; the runtime-socket volume now
  uses `hostPath: /run/k3s`.

## Outcome

OKG is installed and its scale primitive is proven. Next: Phase 4 — Install
KEDA and the observability stack.

</details>

- ✅ `done` — [Phase 4 — Install KEDA and the observability stack](../reference-design/03-step-by-step-implementation/install-keda-and-observability/index.md)

<details markdown="1" class="runbook">
<summary>✅ 📜 Build log — Install KEDA and the observability stack</summary>

# Runbook — Phase 4: Install KEDA and the observability stack

## What was done

Installed the two platform pieces later phases assume are present but no step
actually installs: **KEDA** (the event-driven autoscaler driving the
`GameServerSet` 0↔1 transition) and the **Prometheus/Grafana** stack (the
destination for `mc-monitor` metrics and the alerting home). Installed as
`jyao` on `alpha-games-prd`.

- **KEDA** `2.20.2` → namespace `keda`, helm release `keda`. Operator +
  metrics-apiserver + admission-webhooks all `1/1`. CRDs present incl.
  `scaledobjects.keda.sh`.
- **kube-prometheus-stack** `88.5.4` (Prometheus v3.14.0 + Grafana +
  Alertmanager) → namespace `monitoring`, helm release `prometheus`. All pods
  Running (Alertmanager 2/2, Grafana 3/3, Prometheus 2/2, operator,
  kube-state-metrics, node-exporter).
- **ServiceMonitor** `minecraft-servers` created in the games namespace
  (`prd-games-42wasd-admin`) so Prometheus scrapes `mc-monitor` metrics on the
  `metrics` port. Labels match the kube-prometheus-stack
  `serviceMonitorSelector` (`release: prometheus`).
- Noted the **replica-owner rule**: KEDA must only autoscale *pooled* fleets it
  owns; a named persistent world's `GameServerSet` is owned by the World
  Controller and must **not** get a `ScaledObject`. This phase installs no
  ScaledObject.

## Commands run

```bash
# On host (jyao@alpha) — helm in ~/bin
export PATH=$HOME/bin:$PATH

# KEDA
kubectl create namespace keda
kubectl label namespace keda app.kubernetes.io/managed-by=Helm
kubectl annotate namespace keda \
  meta.helm.sh/release-name=keda meta.helm.sh/release-namespace=keda
helm install keda kedacore/keda --version 2.20.2 --namespace keda

# Prometheus + Grafana (kube-prometheus-stack)
kubectl label namespace monitoring app.kubernetes.io/managed-by=Helm
kubectl annotate namespace monitoring \
  meta.helm.sh/release-name=prometheus meta.helm.sh/release-namespace=monitoring
helm install prometheus prometheus-community/kube-prometheus-stack \
  --version 88.5.4 --namespace monitoring

# ServiceMonitor (from repo, applied to cluster)
kubectl kustomize clusters/alpha | kubectl apply -f -
```

## Verified / observed

- KEDA operator + admission-webhooks + metrics-apiserver `1/1` in `keda`.
- `scaledobjects.keda.sh`, `scaledjobs.keda.sh`, `triggerauthentications.keda.sh`
  CRDs present.
- kube-prometheus-stack pods all Running in `monitoring`; Prometheus v3.14.0
  `Reconciled=True`.
- Services up: Prometheus `9090`, Grafana `80`, Alertmanager `9093`.
- `ServiceMonitor minecraft-servers` created in `prd-games-42wasd-admin`; the
  alpha kustomize build renders it and Prometheus selects it by
  `release: prometheus`.
- Added `keda: 2.20.2` and `kube_prometheus_stack: 88.5.4` to
  `verified-versions.yaml`.
- Marked phase 4 `done` in `progress.yaml` and regenerated
  `docs/implementation/index.md`.

## Outcome

KEDA and the Prometheus/Grafana stack are up; the scrape target exists. Next:
Phase 5 — Deploy CockroachDB and Nakama.

</details>

- ✅ `done` — [Phase 5 — Deploy CockroachDB and Nakama](../reference-design/03-step-by-step-implementation/deploy-cockroachdb-and-nakama/index.md)

<details markdown="1" class="runbook">
<summary>✅ 📜 Build log — Deploy CockroachDB and Nakama</summary>

# Runbook — Phase 5: Deploy CockroachDB and Nakama

## What was done

Deployed **CockroachDB** (Nakama's backing store) and started **Nakama** into
the games namespace `prd-games-42wasd-admin` on `alpha-games-prd`. This phase
was blocked for a long time by a cluster-level Cilium/NetworkPolicy bug, which
was diagnosed, fixed at the platform level in `ubuntu-server-iac`, and
verified live.

### The blocker: pods under default-deny could not reach the kube-apiserver

- **Symptom:** the CockroachDB certificate self-signer job failed with
  `failed to get CA secret: ... Get "https://10.43.0.1:443/api/v1": dial tcp
  10.43.0.1:443: i/o timeout`. No cert Secrets were created.
- **Root cause (proven):** RKE2 runs the kube-apiserver as a **static pod on
  the node**, so the `kubernetes` Service (ClusterIP `10.43.0.1:443`) has its
  backend on the **host node IP** (`192.168.8.132:6443`), not a pod IP. Cilium
  CIDR selectors (`ipBlock`) **ignore node addressing by default**
  (`--policy-cidr-match-mode` excludes `nodes`), so a per-namespace egress
  `default-deny` policy can never be satisfied by an `ipBlock: 0.0.0.0/0` rule —
  the apiserver backend is simply never matched. DNS worked only because
  CoreDNS is a normal pod whose return path stays in-cluster.
- **Fix (authoritative, per Cilium docs):** the `kube-apiserver` **entity**
  represents the apiserver both in-cluster and out-of-cluster. Applied it as a
  **cluster-wide** `CiliumClusterwideNetworkPolicy` so every tenant namespace
  keeps apiserver reachability while remaining default-deny otherwise. Verified
  live: a games-namespace pod reaching `https://10.43.0.1:443/healthz` returned
  `401` (reachable) immediately after the rule applied, and the CRDB
  self-signer then created all three cert Secrets via the API.

## Commands run

```bash
# === On alpha (jyao) ===
export PATH=$HOME/.local/bin:$HOME/bin:$PATH

# 1. Root-cause: confirm default-deny blocks apiserver TCP
kubectl get endpoints kubernetes            # -> 192.168.8.132 (host node IP)
# pod in default namespace (no netpol): https://10.43.0.1/healthz -> 401 OK
# pod in default-deny ns:               dial tcp 10.43.0.1:443 i/o timeout

# 2. Fix (proven live, then committed to ubuntu-server-iac)
kubectl apply -f - <<'EOF'
apiVersion: cilium.io/v2
kind: CiliumClusterwideNetworkPolicy
metadata:
  name: allow-to-kube-apiserver
spec:
  endpointSelector: {}
  egress:
    - toEntities:
      - kube-apiserver
EOF

# 3. CockroachDB install (chart cockroachdb/cockroachdb 21.0.4 / app 26.2.5)
helm install cockroachdb cockroachdb/cockroachdb --version 21.0.4 \
  -n prd-games-42wasd-admin -f ~/crdb-values.yaml

# 4. The first two installs stayed pending because:
#   a) no default StorageClass -> PVC Pending  (fixed: storageClass: nvme-db)
#   b) replicas=1 still used `cockroach start --join=-0,-1,-2` -> never elects
#      itself, readiness probe 503, init job hangs.
#    Fixed with the chart's documented single-node mode:
#      conf.single-node: true  -> pod runs `cockroach start-single-node`
#   (see clusters/alpha/cockroachdb/values.yaml)
helm uninstall cockroachdb -n prd-games-42wasd-admin
kubectl delete pvc datadir-cockroachdb-0 -n prd-games-42wasd-admin --wait=false
helm install cockroachdb cockroachdb/cockroachdb --version 21.0.4 \
  -n prd-games-42wasd-admin -f ~/crdb-values.yaml
```

## Verified / observed

- `cockroachdb-0` `1/1 Running`; StatefulSet `cockroachdb` `1/1` Ready.
- Cert Secrets present (created via API): `cockroachdb-ca-secret`,
  `cockroachdb-node-secret`, `cockroachdb-client-secret`.
- Services `cockroachdb` (headless) and `cockroachdb-public` (ClusterIP) up.
- Nakama deployment present; image needs bumping to 3.40.0 (was stale 3.21.0)
  and needs client certs mounted + TLS config for secure CockroachDB.
- Platform fix in `ubuntu-server-iac`:
  - `infra/kubernetes/platform/networkpolicies/00-allow-kube-apiserver.yaml`
  - `docs/.../default-deny-networkpolicy/index.md` (documents the entity rule)
  - `docs/.../configure-rke2-s-bundled-cilium/index.md`

## Post-audit corrections (2026-08-24)

A phase 0-5 audit against the live cluster found and fixed **two** additional
Nakama blockers that this runbook did not originally capture.

### Correction 1 — Nakama ignores the `NAKAMA_DB_ADDRESS` env var

- **Symptom:** `nakama-migrate` initContainer crash-looped with
  `failed to connect to user=root database=nakama: 127.0.0.1:26257: connection
  refused`.
- **Root cause (proven):** Nakama does **not** read the `NAKAMA_DB_ADDRESS`
  environment variable. The database is configured exclusively via the
  `--database.address` CLI flag (or a YAML config file). The env var is
  silently ignored, so Nakama fell back to its default `root@localhost:26257`
  and could never reach CockroachDB.
- **Fix:** pass the DSN through the command `args` in
  `clusters/alpha/nakama/nakama.yaml`, for **both** the `nakama-migrate`
  initContainer and the main `nakama` container:

  ```yaml
  # initContainer
  command: ["/nakama/nakama"]
  args:
    - "migrate"
    - "up"
    - "--database.address"
    - "root@cockroachdb-public:26257/nakama?sslmode=verify-full&sslrootcert=/certs/ca.crt&sslcert=/certs/tls.crt&sslkey=/certs/tls.key"
  ```

  The main container uses the same `--database.address` in its `args`.

### Correction 2 — `allow-games-egress` ipBlock dropped pod-to-pod traffic

- **Symptom:** even with the correct DSN flag, the migrate init container hung
  (SYN dropped), CockroachDB reported `0/0` client connections, and the pod
  stayed in `Init:0/1` for ~2 minutes then failed.
- **Root cause (proven):** `clusters/alpha/networkpolicy.yaml` defined
  `allow-games-egress` with `egress.to[].ipBlock.cidr: 0.0.0.0/0`. Cilium
  `ipBlock`/CIDR selectors **do not match intra-cluster pod IPs by default**
  (`--policy-cidr-match-mode` excludes `pods`). So `default-deny` silently
  dropped Nakama → CockroachDB (both pods on the same node). This is the same
  Cilium CIDR limitation already documented for node addressing in
  `05-gitops-bootstrap/default-deny-networkpolicy`, applied here to pod IPs.
- **Fix:** replaced the blanket `ipBlock` with explicit label-based egress
  rules in `clusters/alpha/networkpolicy.yaml`:

  ```yaml
  egress:
    # Nakama -> CockroachDB
    - to:
        - podSelector:
            matchLabels:
              app.kubernetes.io/name: cockroachdb
      ports:
        - protocol: TCP
          port: 26257
    # Velocity -> Paper lobby
    - to:
        - podSelector:
            matchLabels:
              app: paper-lobby
      ports:
        - protocol: TCP
          port: 25565
  ```

  DNS is already granted by the platform `allow-cluster-dns`, and the
  kube-apiserver by the cluster-wide `allow-to-kube-apiserver` CCNP, so neither
  is duplicated here.

### Verified after corrections

- Nakama `2/2` Ready and `Available`; logs show `"Startup done"`, gRPC API on
  7349, HTTP gateway 7350, console 7351 — it connected to CockroachDB and ran
  the schema migration successfully.
- `kubectl get deploy nakama -n prd-games-42wasd-admin` → `2/2`.

</details>

- ⬜ `not-started` — [Phase 6 — Deploy Velocity](../reference-design/03-step-by-step-implementation/deploy-velocity/index.md)

<details markdown="1" class="runbook">
<summary>⬜ 📜 Build log — Deploy Velocity</summary>

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

</details>

- ⬜ `not-started` — [Phase 7 — Deploy the Paper lobby](../reference-design/03-step-by-step-implementation/deploy-the-paper-lobby/index.md)

<details markdown="1" class="runbook">
<summary>⬜ 📜 Build log — Deploy the Paper lobby</summary>

# Runbook — Phase 7: Deploy the Paper lobby

Deployed the **Paper lobby** (the always-on home world behind Velocity) into
`prd-games-42wasd-admin` on `alpha`. It ended `1/1 Running`. This write-up
records the two real failure modes hit — a namespace default LimitRange OOM,
and a **Java 25 + Spark async-profiler native crash** — plus the
storage-controller non-issue that looked like the cause but wasn't.

## What was done

- **Paper lobby** (`clusters/alpha/lobby/paper.yaml`):
  - Added a `10Gi` `nvme-fast` RWO PVC (`paper-lobby-data`).
  - Explicit `resources` (`requests.memory: 2Gi`, `limits.memory: 8Gi`) plus
    `MEMORY=4G` heap — without them the namespace LimitRange defaulted to
    `1Gi`, and world generation was **OOMKilled (exit 137)**.
  - **Java 21 image** `itzg/minecraft-server:2026.8.2-java21`.
  - Recreate strategy (RWO single-node volume ⇒ rolling updates deadlock; see
    the storage-controller note below).

## Failure 1 — paper-lobby OOMKilled (exit 137)

The namespace LimitRange `container-defaults` sets `default.memory: 1Gi`.
Paper 1.21 world generation exceeds that and the container was OOM-killed
mid-`Preparing level "world"`, with no Java error (just exit 137).

**Fix:** explicit `resources.requests.memory: 2Gi` / `resources.limits.memory:
8Gi` (under the LimitRange `max` of 8Gi) and `MEMORY=4G` heap in the container
spec. The 4Gi pod limit originally used was too tight because the JVM heap is
only part of process memory (metaspace + thread stacks + native + GC overhead),
so heap `4G` + overhead exceeded it — hence `limits.memory: 8Gi` (2× heap) for
safe headroom.

## Failure 2 — JVM native SIGSEGV in Spark's async-profiler (Java 25)

After the OOM was fixed, the server got to `Done (37s)!` then crashed:

```
# SIGSEGV (0xb) at pc=0x0000000000000000
# JRE: Temurin-25.0.4+7
# Problematic frame:
# C [spark-...-libasyncProfiler.so.tmp+0x270e9]  VMThread::nativeThreadId(...)
# Current thread: JavaThread "Async-profiler Timer"
```

**Root cause (researched, authoritative):** lucko/spark **Issue #565
"Support Linux with Java25"** — Spark's bundled async-profiler native engine
crashes the JRE on **Java 25** on Linux the moment the profiler starts (which
Paper does ~37s after boot). The issue author confirms the intended JRE is
**Java 21**.

**Fix:** switch the image to the Java 21 build of the same release tag
(`2026.8.2-java21`). No `SPARK=false` workaround needed.

## Storage controller — NOT the problem (important)

The `verifyMount: device already mounted` / `can not mount, volume already
mounted` errors in the OpenEBS LVM plugin were **correct RWO enforcement**,
not a controller fault. During a Deployment RollingUpdate two pods briefly
coexist; the second one asks to mount the same single-node RWO volume the
first still holds, and the LVM plugin correctly refuses. On a one-node cluster
with an RWO PVC, a rolling update therefore deadlocks — always use a clean
delete → apply for such deployments.

## Commands run

```bash
# === On alpha (jyao) ===
export PATH=$PATH:$HOME/bin

# Paper-lobby — OOM fix + Java 21 (clean re-deploy, avoids RWO concurrent mount)
kubectl -n prd-games-42wasd-admin delete deployment paper-lobby
kubectl -n prd-games-42wasd-admin wait --for=delete pod -l app=paper-lobby --timeout=60s
kubectl apply -f clusters/alpha/lobby/paper.yaml
kubectl -n prd-games-42wasd-admin rollout status deployment/paper-lobby
```

## Verified / observed

- `paper-lobby` `1/1 Running`, 0 restarts, `Done (32.66s)!`, past the 37s
  Java 25 crash window on Java 21.
- Reached by velocity via `paper-lobby.prd-games-42wasd-admin.svc.cluster.local:25565`
  (`LOBBY-OPEN`; see the Phase 6 runbook).

---

# Phase — Import the missing multi-world data into the lobby PVC

## Symptom

The spawn system was not working. On every join Multiverse logged
`Failed to teleport player <name> on join: Failure{reason=NULL_LOCATION}`,
LobbyGames loaded **0 arenas**, and DecentHolograms couldn't resolve a
`spawn` world.

## Root cause — worlds missing from the PVC

The lobby PVC (`paper-lobby-data`, 10Gi) only contained the vanilla worlds
`world`, `world_nether`, `world_the_end`. The rest of the network's
**multi-world setup** — `spawn`, `creative_plots`, `Arcade`, `hub` — was
never copied into the PVC (the source had previously lived on a separate host
at `/home/jyao-42admin/42wasd-mc/world-data/`, a large server-data dir
gitignored by the repo). Multiverse-Core is configured (`join-destination:
spawn`) to send every joining player to the `spawn` world, so with that world
missing every spawn-related plugin failed:

```text
[Multiverse-Core] Failed to autoload world spawn: WORLD_FOLDER_INVALID
[Multiverse-Core] Failed to autoload world creative_plots: WORLD_FOLDER_INVALID
[Multiverse-Core] Failed to autoload world Arcade: WORLD_FOLDER_INVALID
[LobbyGames] Loaded 0 arenas!
[DecentHolograms] Cannot retrieve World from value spawn!
[20:06:39] [Multiverse-Core] Failed to teleport player jya0 on join: NULL_LOCATION
```

## Fix — rsync the missing worlds from the source host into the PVC

The authoritative full data dir is `/home/jyao-42admin/42wasd-mc/world-data/`
(gitignored; large binaries managed outside Git). The PVC is a host
`nvme-fast` LVM volume mounted at
`/var/lib/kubelet/pods/<pod-uuid>/volumes/kubernetes.io~csi/pvc-<id>/mount`.

Commands run (on alpha, via sudo):

```bash
# Locate the PVC host mount (matches pvc-c64d03bc-... = paper-lobby-data)
mount | grep pvc-c64d03bc

# Copy the 4 missing worlds and set ownership to the pod's UID (1000)
PVC=/var/lib/kubelet/pods/<pod-uuid>/volumes/kubernetes.io~csi/pvc-c64d03bc.../mount
SRC=/home/jyao-42admin/42wasd-mc/world-data
for d in spawn creative_plots Arcade hub; do
  rsync -a "$SRC/$d/" "$PVC/$d/"
done
chown -R 1000:1000 "$PVC/spawn" "$PVC/creative_plots" "$PVC/Arcade" "$PVC/hub"

# Restart the lobby so Multiverse loads the new worlds
kubectl -n prd-games-42wasd-admin rollout restart deployment/paper-lobby
kubectl -n prd-games-42wasd-admin rollout status deployment/paper-lobby
```

## Verified / observed

- `spawn` (129M), `creative_plots` (47M), `Arcade` (44M), `hub` (228K) now
  present in the PVC.
- Worlds autoload cleanly: `[WorldGuard] Loaded configuration for world 'spawn'`
  / `'creative_plots'`; `Prepared spawn area`.
- **`[LobbyGames] Loaded 7 arenas!`** (was 0).
- **`[DecentHolograms] Loaded 5 holograms!`**.
- No more `WORLD_FOLDER_INVALID`, `NULL_LOCATION`, or `Failed to teleport` in
  the logs.

## Note on the login plugin

The user originally asked to remove a login plugin (AuthMe) from the lobby PVC
— the `/login`/`/register` password plugin — but after the investigation chose
to **not remove** it and instead fix the spawn/world issue. AuthMe
(`AuthMe-5.7.0.jar`) and VerifyMC (email whitelist plugin) remain installed.

</details>

- ⬜ `not-started` — [Phase 8 — Install TAB](../reference-design/03-step-by-step-implementation/install-tab/index.md)
- ⬜ `not-started` — [Phase 9 — Add ViaVersion and ViaBackwards](../reference-design/03-step-by-step-implementation/add-viaversion-and-viabackwards/index.md)
- ⬜ `not-started` — [Phase 10 — Deploy the Forge 1.20.1 fantasy runtime](../reference-design/03-step-by-step-implementation/deploy-the-forge-1-20-1-fantasy-runtime/index.md)
- ⬜ `not-started` — [Phase 11 — Define the runtime catalog](../reference-design/03-step-by-step-implementation/define-the-runtime-catalog/index.md)
- ⬜ `not-started` — [Phase 12 — Define map metadata](../reference-design/03-step-by-step-implementation/define-map-metadata/index.md)
- ⬜ `not-started` — [Phase 13 — Build the World Controller](../reference-design/03-step-by-step-implementation/build-the-world-controller/index.md)
- ⬜ `not-started` — [Phase 14 — Build NetworkBridge for Velocity](../reference-design/03-step-by-step-implementation/build-networkbridge-for-velocity/index.md)
- ⬜ `not-started` — [Phase 15 — Implement friends and parties](../reference-design/03-step-by-step-implementation/implement-friends-and-parties/index.md)
- ⬜ `not-started` — [Phase 16 — Implement `/join <friend>`](../reference-design/03-step-by-step-implementation/implement-join-friend/index.md)
- ⬜ `not-started` — [Phase 17 — Implement pending cross-runtime invites](../reference-design/03-step-by-step-implementation/implement-pending-cross-runtime-invites/index.md)
- ⬜ `not-started` — [Phase 18 — Publish Modrinth Server Projects](../reference-design/03-step-by-step-implementation/publish-modrinth-server-projects/index.md)
- ⬜ `not-started` — [Phase 19 — Add packwiz CI](../reference-design/03-step-by-step-implementation/add-packwiz-ci/index.md)
- ⬜ `not-started` — [Phase 20 — Add exact world/dimension TAB information](../reference-design/03-step-by-step-implementation/add-exact-world-dimension-tab-information/index.md)
- ⬜ `not-started` — [Phase 21 — Implement the glitch/random portal](../reference-design/03-step-by-step-implementation/implement-the-glitch-random-portal/index.md)
- ⬜ `not-started` — [Phase 22 — Add mc-router](../reference-design/03-step-by-step-implementation/add-mc-router/index.md)
- ⬜ `not-started` — [Phase 23 — Add idle sleep](../reference-design/03-step-by-step-implementation/add-idle-sleep/index.md)
- ⬜ `not-started` — [Phase 24 — Add Agones only for session worlds](../reference-design/03-step-by-step-implementation/add-agones-only-for-session-worlds/index.md)
- ⬜ `not-started` — [Phase 25 — Add AI proximity chat](../reference-design/03-step-by-step-implementation/add-ai-proximity-chat/index.md)
- ⬜ `not-started` — [Phase 26 — Add object storage for the community upload pipeline](../reference-design/03-step-by-step-implementation/add-object-storage/index.md)
- ⬜ `not-started` — [Phase 27 — Community map upload pipeline](../reference-design/03-step-by-step-implementation/community-map-upload-pipeline/index.md)
- ⬜ `not-started` — [Phase 28 — Backups](../reference-design/03-step-by-step-implementation/backups/index.md)
- ⬜ `not-started` — [Phase 29 — Monitoring](../reference-design/03-step-by-step-implementation/monitoring/index.md)
- ⬜ `not-started` — [Phase 30 — Rollout order](../reference-design/03-step-by-step-implementation/rollout-order/index.md)

<!-- END_GENERATED_IMPLEMENTATION -->