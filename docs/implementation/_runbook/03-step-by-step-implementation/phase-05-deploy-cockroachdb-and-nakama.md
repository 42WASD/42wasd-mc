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