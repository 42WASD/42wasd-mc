---
phase: 03-step-by-step-implementation/add-mc-router
---
# Phase 10 — Add mc-router (hostname routing at the public edge)

Phase 22 of the reference design, promoted ahead of schedule. This is the
change that makes *"type the address and it just works"* true: a player enters
a bare hostname and reaches the intended world, with no port number and no SRV
record.

Supersedes the exposure decision in **Phase 9 (Deploy the ATM10SKY modded
server)** — ATM10SKY is no longer a standalone NodePort. Runbook content is
inlined into `docs/implementation/index.md`, so sibling runbooks are referenced
by name rather than linked (a `./phase-09-*.md` relative link would not resolve
from the generated page).

## 1. Why a hostname router is required

The public relay (`89.36.162.171`) multiplexes by **L4 port**. A DNS name
resolving to that IP changes nothing, because NAT never sees a hostname:

```text
mc-oompas.42base.com  ── A ──>  89.36.162.171
                                      │
                     relay DNAT by port only (30000-30199, 25565)
```

`mc-router` solves this by parsing the **Minecraft handshake packet**, which
literally contains the hostname the player typed, then proxying the raw TCP
stream to the right backend:

```text
one public IP : one public port : many worlds
```

Crucially it does **not** speak Minecraft beyond that handshake — no Velocity,
no mod compatibility, no forwarding config. That is why it can front a NeoForge
1.21.1 world and a Paper 1.21.10 proxy simultaneously, which Velocity cannot
(`/join` cannot cross incompatible protocol versions).

## 2. Topology before and after

**Before** — two public NodePorts, hostname irrelevant:

```text
relay :25565  -> 10.200.0.2:30079  -> velocity  (NodePort)  -> paper-lobby
relay :30080  -> 10.200.0.2:30080  -> atm10sky  (NodePort)
```

**After** — one public port, dispatched by hostname:

```text
relay :25565 -> 10.200.0.2:30079 -> mc-router (only NodePort)
                                     ├─ "mc-oompas.42base.com" -> atm10sky   (ClusterIP)
                                     ├─ "minecraft.42base.com" -> velocity   (ClusterIP)
                                     └─ anything else          -> velocity   (default)
```

The relay needed **no change**: it already DNATs `:25565 -> 10.200.0.2:30079`.
DNAT rewrites IP headers only, never the payload, so the hostname arrives intact
and survives the WireGuard tunnel.

## 3. Public boundary now enforced, not just documented

The reference design is explicit (§16 "Public network boundary"):

> Expose only `Velocity / mc-router Minecraft entry` … **Backends remain private
> `ClusterIP` services**.
> `[ ] lobby cannot be reached directly from public Internet`

Both backends had NodePorts, so that acceptance criterion failed — anyone
knowing the relay IP could bypass the edge entirely. Both are now `ClusterIP`.

Verify exactly one public door remains:

```bash
kubectl kustomize clusters/alpha > /tmp/rendered.yaml
python3 - <<'EOF'
import yaml
docs = [d for d in yaml.safe_load_all(open('/tmp/rendered.yaml')) if d]
bad = []
for d in docs:
    if d.get('kind') == 'Service':
        t = d['spec'].get('type', 'ClusterIP')
        nps = [p.get('nodePort') for p in d['spec']['ports'] if p.get('nodePort')]
        print(f"  {d['metadata']['name']:22s} {t:11s} nodePorts={nps}")
        if t == 'ClusterIP' and nps:
            bad.append(d['metadata']['name'])
print("\nERROR: ClusterIP with nodePort:", bad if bad else "none")
EOF
```

```text
  atm10sky               ClusterIP   nodePorts=[]
  cockroachdb-public     ClusterIP   nodePorts=[]
  mc-router              NodePort    nodePorts=[30079]
  nakama                 ClusterIP   nodePorts=[]
  paper-lobby            ClusterIP   nodePorts=[]
  velocity               ClusterIP   nodePorts=[]

ERROR: ClusterIP with nodePort: none
```

## 4. Static MAPPING, not Kubernetes service discovery

The image supports discovering annotated Services (`--in-kube-cluster` +
`mc-router.itzg.me/externalServerName`). Deliberately **not** used:

- discovery needs a `ClusterRole` granting `watch`/`list` on Services — broad
  read access to the whole cluster for a TCP proxy;
- the routing table would live in scattered annotations instead of one
  reviewable file;
- any Service annotated by mistake would become publicly routable.

Static env keeps the entire public surface in `clusters/alpha/mc-router/mc-router.yaml`:

```yaml
- name: MAPPING
  value: >-
    mc-oompas.42base.com=atm10sky.prd-games-42wasd-admin.svc.cluster.local:25565,
    minecraft.42base.com=velocity.prd-games-42wasd-admin.svc.cluster.local:25565
- name: DEFAULT
  value: velocity.prd-games-42wasd-admin.svc.cluster.local:25565
```

Switch to discovery only when scale-to-zero worlds land, since native 0↔1
autoscaling requires watching a **StatefulSet**.

## 5. NetworkPolicy: ingress moves to the edge

Kubernetes NetworkPolicy is **bidirectional** — an egress allow on the source is
useless without a matching ingress allow on the destination. With the backends
now private, the old `allow-games-ingress` (velocity, *no* `from:` = any source)
had to be replaced.

`allow-games-ingress` and `allow-atm10sky-ingress` were **deleted** and replaced
by one policy whose peer set *is* the public boundary:

```yaml
name: allow-mc-router-to-game-backends
podSelector:            # velocity + atm10sky
  matchExpressions:
    - {key: app, operator: In, values: [velocity, atm10sky]}
ingress:
  - from:
      - podSelector:
          matchLabels: {app: mc-router}
    ports: [{protocol: TCP, port: 25565}]
```

Egress uses **pod label selectors, never `ipBlock`**. In Cilium, `ipBlock`/CIDR
selectors do not match in-cluster pod IPs by default, so
`ipBlock: 0.0.0.0/0` would silently drop the forward to velocity/atm10sky.

## 6. Deployment sequence

Port `30079` had to be released before mc-router could claim it — a NodePort is
exclusively allocated. Applying the new manifests while `velocity` still held it
failed outright:

```text
The Service "mc-router" is invalid: spec.ports[0].nodePort: Invalid value:
30079: provided port is already allocated
```

So: release, then apply.

```bash
# 1) release both NodePorts
kubectl -n prd-games-42wasd-admin patch svc velocity --type merge -p \
  '{"spec":{"type":"ClusterIP","ports":[{"name":"minecraft","port":25565,"targetPort":25565,"protocol":"TCP"}]}}'
kubectl -n prd-games-42wasd-admin patch svc atm10sky --type merge -p \
  '{"spec":{"type":"ClusterIP","ports":[{"name":"minecraft","port":25565,"targetPort":25565,"protocol":"TCP"}]}}'

# 2) confirm free
kubectl get svc -A -o json | python3 -c '
import sys,json
d=json.load(sys.stdin)
print([(p.get("nodePort"),s["metadata"]["name"]) for s in d["items"]
       for p in s["spec"].get("ports",[]) if p.get("nodePort") in (30079,30080)])'
# -> []  (free)

# 3) render + apply
kubectl kustomize clusters/alpha > /tmp/rendered.yaml
kubectl apply -f /tmp/rendered.yaml
kubectl -n prd-games-42wasd-admin rollout status deploy/mc-router --timeout=120s
```

```text
deployment "mc-router" successfully rolled out
```

## 7. Failure encountered: Argo selfHeal reverted the live apply

Manifests were applied live *before* committing. `tenant-games-alpha` runs
`automated: {prune: true, selfHeal: true}`, so within ~60 s Argo reconciled back
to the last commit (`62f4f86`) and **pruned the mc-router Service**, restoring
both NodePorts:

```text
Updated sync status: OutOfSync -> Synced
OperationStarted: Initiated automated sync to '62f4f863...'
Partial sync operation succeeded
```

```text
$ kubectl -n prd-games-42wasd-admin get svc mc-router
Error from server (NotFound): services "mc-router" not found
```

**Rule:** in this repo, a live `kubectl apply` is not a deployment — it is a
temporary state that Argo will delete. Commit and push first, then let Argo
sync (or sync explicitly). This is the same class of surprise as the earlier
`platform-root` selfHeal reverting manual Application patches.

## 8. Verification: hostname dispatch

A plain DNS lookup or TCP connect **cannot** test this — both hostnames share
one IP and one port. You must connect to the router's address while putting a
*chosen* hostname inside the handshake, which is the only way to prove the
router reads L7.

`/tmp/mcping_host.py <connect-host> <port> <handshake-hostname>`:

```bash
python3 mcping_host.py 192.168.8.240 30079 mc-oompas.42base.com  "[expect ATM10SKY]"
python3 mcping_host.py 192.168.8.240 30079 minecraft.42base.com  "[expect Velocity]"
python3 mcping_host.py 192.168.8.240 30079 unknown.example.com   "[expect default]"
```

## 9. Operational notes

- **Two replicas.** This is the single public entry for every world; a restart
  must not black-hole the network. Both are stateless — the table comes from env
  and each replica forwards long-lived TCP streams independently.
- **Probe noise is expected.** kubelet `tcpSocket` probes connect and close
  without a handshake, so the logs show
  `level=error msg="Failed to read packet" error=EOF` every cycle. Harmless.
- **REST API** on `:8081` (`GET /routes`) for debugging; prometheus metrics via
  `METRICS_BACKEND=prometheus`. Not exposed publicly.
- **Rate limit** raised to 5/s: the upstream default of 1/s throttles a client
  refreshing the server list, while still defeating port scanners (which
  mc-router additionally blocks outright, since it refuses connections whose
  handshake names no mapped hostname).
- **Pinned** `itzg/mc-router:1.54.2`. A floating `latest` would silently change
  the public edge on any pod restart.

> **Status:** complete. `mc-oompas.42base.com` → ATM10SKY and
> `minecraft.42base.com` → Velocity, both on the single public port 25565 with
> no port typed by the player. Backends are ClusterIP-only, so the reference
> design's public boundary is now enforced by NetworkPolicy rather than merely
> documented.
