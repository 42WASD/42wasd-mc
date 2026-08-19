# Step 2 — Secure forwarding + backend isolation

Prove that identity survives the proxy → backend hop (modern forwarding) and that backends are unreachable from the public internet.

## Goal

The authenticated UUID seen by Velocity is the same UUID the backend sees, and the backend is isolated behind the proxy.

## Tasks

### 1. Create the forwarding secret

Generate a strong random secret and store it as a Kubernetes Secret. **Never commit it to Git.**

```bash
openssl rand -base64 48
```

```bash
kubectl create secret generic velocity-forwarding \
  --namespace minecraft-system \
  --from-literal=secret="$(openssl rand -base64 48)"
```

### 2. Enable modern forwarding on Velocity

```toml
player-info-forwarding-mode = "modern"
forwarding-secret-file = "forwarding.secret"
```

Mount the secret as `forwarding.secret` in the Velocity container.

### 3. Configure the Paper lobby for modern forwarding

`server.properties`:

```properties
online-mode=false
```

`spigot.yml`:

```yaml
settings:
  bungeecord: false
```

`config/paper-global.yml`:

```yaml
proxies:
  velocity:
    enabled: true
    online-mode: true
    secret: "THE_SAME_FORWARDING_SECRET"
```

Prefer mounting the secret rather than writing it into Git.

### 4. Make backends private

- Backend Services must be **ClusterIP** (not `LoadBalancer`, not `NodePort`).
- Add a network policy allowing only Velocity → lobby on port 25565.
- Expose only the proxy via the public endpoint.

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-private
  namespace: minecraft
spec:
  podSelector:
    matchLabels:
      app: lobby
  policyTypes: [Ingress]
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: minecraft-system
      ports:
        - protocol: TCP
          port: 25565
```

## Acceptance criteria

```text
[ ] player UUID seen by backend == authenticated UUID seen by Velocity
[ ] lobby Service is ClusterIP
[ ] network policy only allows the proxy namespace to reach the backend
[ ] the forwarding secret is stored as a Secret, not in Git
```

## Why this matters

Backends run in `online-mode=false`. If a backend is reachable publicly, anyone can join with a spoofed identity. Modern forwarding + network isolation are what make that acceptable.

## Next step

[Step 3 — TAB](step-03-tab.md)