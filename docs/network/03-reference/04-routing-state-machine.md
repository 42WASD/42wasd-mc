# Routing state machine

```text
REQUESTED
    │
    ├── incompatible runtime ─────► CLIENT_TRANSITION_REQUIRED
    │
    └── compatible
            │
            ▼
         RESERVING
            │
            ▼
         STARTING
            │
            ▼
     WAITING_K8S_READY
            │
            ▼
      WAITING_MC_READY
            │
            ▼
        REGISTERING
            │
            ▼
         TRANSFERRING
            │
            ├── success ─────────► COMPLETE
            │
            └── failure ─────────► RELEASE_RESERVATION -> FAILED
```

Every stage should have timeout/error handling.