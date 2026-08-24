# clusters/

Kubernetes configuration, one directory per environment cluster.

```text
clusters/
└── alpha/                     # alpha-games-prd (RKE2, GitOps via Argo CD)
    ├── namespace.yaml         # games namespace (prd-games-42wasd-admin)
    ├── kustomization.yaml     # aggregate of the platform components
    ├── velocity/              # Velocity proxy (front door)
    ├── lobby/                 # paper lobby runtime (lobby-1)
    ├── nakama/                # social/identity backend
    ├── cockroachdb/           # Nakama backing store
    ├── mc-router/             # hostname -> server routing (planned)
    └── monitoring/            # observability (planned)
```

Each component directory is a kustomize base that the parent
`kustomization.yaml` aggregates. Namespaces and IDs follow the naming
convention decided in Phase 0.