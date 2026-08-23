# Create Kubernetes namespaces

Starter:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: minecraft
---
apiVersion: v1
kind: Namespace
metadata:
  name: minecraft-system
```

Suggested separation:

```text
minecraft
  -> actual game servers

minecraft-system
  -> proxy, world-controller, NetworkBridge, mc-router,
     CockroachDB, Nakama
```

If you already have tenant-specific namespace policy, adapt this rather than bypassing it.

Apply:

```bash
kubectl apply -f clusters/alpha/namespace.yaml
```

---
