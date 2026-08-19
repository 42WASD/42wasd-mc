# Phase 4 — Deploy Velocity

## Use Java 25

Current PaperMC documentation requires Java 25. If using `itzg/mc-proxy`, use its Java 25 variant.

Example conceptual Deployment:

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

**Production note:** pin the image digest or tested release tag after validation.

## Create a forwarding secret

Generate a strong random secret:

```bash
openssl rand -base64 48
```

Store it as a Kubernetes Secret. Do **not** commit it to Git.

Velocity:

```toml
player-info-forwarding-mode = "modern"
forwarding-secret-file = "forwarding.secret"
```

## Configure an initial backend

Start with exactly one backend:

```toml
[servers]
lobby = "lobby.minecraft.svc.cluster.local:25565"

try = ["lobby"]
```

Do not begin with dynamic registration before static connectivity works.

## Public exposure

Expose Velocity, not backend servers.

```text
Internet → Velocity Service / relay → ClusterIP Minecraft backend
```

Acceptance criteria:

```text
[ ] public client reaches Velocity
[ ] player authenticates in online mode at proxy
[ ] lobby cannot be reached directly from public Internet
```