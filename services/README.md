# services/

Custom platform services that glue the Minecraft network together (as opposed
to off-the-shelf images in `clusters/`).

```text
services/
├── world-controller/    # scales worlds to zero / on-demand (OKG)
└── network-bridge/      # cross-service connectivity / relay
```

Each service lives in its own directory with source, Dockerfile, and any
manifests. These are the pieces the reference design marks as "build"
rather than "adopt".