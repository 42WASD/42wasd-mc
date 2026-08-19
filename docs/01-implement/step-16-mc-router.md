# Step 16 — mc-router edge wake

Expose the proxy through **mc-router** at the network edge so that the proxy is reachable, and — importantly — extend the wake behavior so a connection to a sleeping backend at the edge triggers a wake rather than being refused.

## Goal

The public edge routes to the proxy correctly, and a player connecting while a target backend is asleep is handled by the wake flow rather than getting disconnected.

## Tasks

### 1. Deploy mc-router at the edge

- Deploy `mc-router` in front of (or beside) Velocity to route the public `play.example.com` to the proxy service.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mc-router
  namespace: minecraft-system
spec:
  selector:
    matchLabels:
      app: mc-router
  template:
    metadata:
      labels:
        app: mc-router
    spec:
      containers:
        - name: mc-router
          image: itzg/mc-router:latest
          args: ["--default=velocity.minecraft-system.svc.cluster.local:25577"]
```

### 2. Handle sleeping backends at the edge

- The router or proxy must detect "target backend asleep" and fall back to the wake flow (Step 9/10) instead of a dead drop.

### 3. Verify public reachability + wake

Connect from outside; confirm a sleep-backend connection is put into the wake-and-wait path.

## Acceptance criteria

```text
[ ] public host routes through mc-router to the proxy
[ ] connecting to a sleeping backend triggers wake (not disconnect)
[ ] existing wake/wait/transfer flow works from the edge
[ ] edge DNS/service config matches the proxy service name
```

## Next step

[Step 17 — Community map upload pipeline](step-17-map-upload.md)