---
phase: 03-step-by-step-implementation/incident-recover-prod-games
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