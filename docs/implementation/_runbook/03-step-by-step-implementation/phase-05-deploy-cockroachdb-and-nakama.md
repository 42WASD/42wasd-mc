---
phase: 03-step-by-step-implementation/deploy-cockroachdb-and-nakama
---

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