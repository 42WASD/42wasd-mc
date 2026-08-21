# Phase 1 — Create repository structure

Recommended Git repository:

```text
minecraft-platform/
├── README.md
├── clusters/
│   └── alpha/
│       ├── namespace.yaml
│       ├── velocity/
│       ├── nakama/
│       ├── cockroachdb/
│       ├── mc-router/
│       └── monitoring/
├── runtimes/
│   ├── vanilla-current/
│   │   ├── runtime.yaml
│   │   └── server/
│   ├── backrooms-current/
│   │   ├── runtime.yaml
│   │   └── server/
│   └── fantasy-1.20.1-forge/
│       ├── runtime.yaml
│       ├── packwiz/
│       └── server/
├── maps/
│   ├── survival-main/
│   │   └── map.yaml
│   └── backrooms-level-0/
│       └── map.yaml
├── services/
│   ├── world-controller/
│   └── network-bridge/
└── docs/
```

Goal:

```text
Git says what SHOULD exist.
Kubernetes says what IS running.
Nakama says what PLAYERS are doing.
```

---
