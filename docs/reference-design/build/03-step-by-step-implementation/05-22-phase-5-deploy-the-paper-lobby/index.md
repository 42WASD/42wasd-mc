# Phase 5 — Deploy the Paper lobby

Use `itzg/minecraft-server`.

Conceptual StatefulSet:

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

Backend offline mode is acceptable **only because the backend is private behind the authenticated proxy**.

---

## 22.1 Configure Paper modern forwarding

Current PaperMC guidance:

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

Prefer templating/mounting the secret rather than writing it into Git.

---

## 22.2 Verify identity

Inside lobby:

```text
player UUID seen by backend
==
authenticated UUID seen by Velocity
```

If not, stop and fix forwarding before adding social state.

---
