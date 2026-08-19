# Step 1 — Velocity + static Paper lobby

The foundation: a public proxy in front of a single static Paper lobby. Nothing dynamic yet — this proves the basic network, auth, and player flow.

## Goal

A vanilla Minecraft player can connect to the public address, authenticate through the proxy, and land in a Paper lobby — and the lobby is **not** directly reachable from the public internet.

## Prerequisites

- A working Kubernetes cluster with `kubectl` access.
- `git`, `uv`, `kubectl`, and `openssl` available.
- The [naming conventions](../01-implement/index.md#naming-convention-step-1-prerequisite) decided.

## Tasks

### 1. Create namespaces

```bash
kubectl apply -f - <<'EOF'
apiVersion: v1
kind: Namespace
metadata:
  name: minecraft
---
apiVersion: v1
kind: Namespace
metadata:
  name: minecraft-system
EOF
```

### 2. Deploy Velocity (proxy)

Velocity 4.x requires **Java 25**, so use the `itzg/mc-proxy` Java 25 variant.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: velocity
  namespace: minecraft-system
spec:
  replicas: 1
  selector:
    matchLabels:
      app: velocity
  template:
    metadata:
      labels:
        app: velocity
    spec:
      containers:
        - name: velocity
          image: itzg/mc-proxy:java25
          env:
            - name: TYPE
              value: VELOCITY
            - name: MEMORY
              value: 1G
          ports:
            - containerPort: 25577
              name: minecraft
```

> **Pin the image** digest or a tested release tag before production — do not rely on a floating tag.

### 3. Deploy the Paper lobby

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: lobby
  namespace: minecraft
spec:
  serviceName: lobby
  replicas: 1
  selector:
    matchLabels:
      app: lobby
  template:
    metadata:
      labels:
        app: lobby
    spec:
      containers:
        - name: minecraft
          image: itzg/minecraft-server:2026.8.0
          env:
            - name: EULA
              value: "TRUE"
            - name: TYPE
              value: "PAPER"
            - name: ONLINE_MODE
              value: "FALSE"
          ports:
            - containerPort: 25565
```

Backend `online-mode=false` is acceptable **only because** the backend is private behind the proxy (this is fully locked down in Step 2).

### 4. Configure Velocity with one static backend

In the Velocity config, point to the lobby only:

```toml
[servers]
lobby = "lobby.minecraft.svc.cluster.local:25565"

try = ["lobby"]
```

### 5. Expose the proxy

Expose only **Velocity**, never the lobby. In front of the cluster, route your public host (`play.example.com`) to the Velocity service port `25577`.

## Acceptance check

```text
[ ] public client reaches Velocity
[ ] player authenticates in online mode at the proxy
[ ] lobby cannot be reached directly from the public internet
```

## Common mistakes

- Backend exposed publicly (fix in Step 2 with ClusterIP + network policy).
- No EULA or wrong image tag.
- Connecting clients to the backend port instead of the proxy.

## Next step

[Step 2 — Secure forwarding + backend isolation](step-02-forwarding-isolation.md)