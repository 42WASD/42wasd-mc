# Argo CD bootstrap

Installs Argo CD into the cluster and registers the "platform" and "tenants"
application-of-applications roots.

- `install.yaml` / `kustomization.yaml` — Argo CD core (manifests + namespaces).
- `apps-of-apps.yaml` — registers the platform and tenants root Applications
  that Argo CD then reconciles to drive the whole Minecraft network.

> **TODO**: fill `repoURL`, `targetRevision`, and paths once the git repo is
> hosting `infra/kubernetes/`. See `docs/` for the platform architecture.