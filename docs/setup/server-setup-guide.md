# Server Setup Guide

A practical, ordered walkthrough for standing up the Minecraft network. For the
full conceptual background, read the
[Reference Design](../reference-design/index.md) first; for exact
configuration detail on each component, see the corresponding build phase.

## 1. Prerequisites

- A Kubernetes cluster (managed or self-hosted) with persistent volumes.
- `kubectl` configured for your cluster.
- `uv` for the docs/tooling environment.
- DNS that you can point at the proxy's public address (e.g. `play.example.com`).

## 2. Foundation (Phases 1–3)

1. **Decide names** — pick runtime IDs (`vanilla-current`, `backrooms-current`,
   `fantasy-1.20.1-forge`, `experimental-*`), a public host, and a namespace
   convention (`minecraft`, `minecraft-system`).
2. **Create namespaces** in the cluster.
3. **Deploy CockroachDB and Nakama** — Nakama 3.40.0 with CockroachDB as its
   backing store, used for identity, friends, and parties.

## 3. Core proxy + backends (Phases 4–7)

4. **Deploy Velocity** (Java 25) with a forwarding secret.
5. **Deploy the Paper lobby** with modern forwarding (online-mode at the proxy,
   offline at the backend).
6. **Install TAB** for network-wide presence.
7. **Add ViaVersion/ViaBackwards** for protocol compatibility.

## 4. Fantasy runtime + control plane (Phases 8–12)

8. **Deploy the Forge 1.20.1 fantasy runtime** and pin it.
9. **Define the runtime catalog** — the standardized runtime classes.
10. **Define map metadata** — which runtime each map requires.
11. **Build the World Controller** — the routing + wake brain.
12. **Build NetworkBridge** — lets Velocity talk to the controller.

## 5. Social (Phases 13–18)

13. **Friends and parties** on Nakama.
14. **`/join <friend>`**.
15. **Pending cross-runtime invites**.
16. **Publish Modrinth Server Projects**.
17. **Add packwiz CI**.
18. **Exact world/dimension TAB** information.

## 6. Dynamic routing (Phases 19–24)

19. **The glitch/random portal**.
20. **mc-router** at the edge.
21. **Idle sleep** (scale-to-zero).
22. **Agones** for session worlds (optional).
23. **AI proximity chat**.
24. **Community map upload pipeline**.

## 7. Operate (Phases 25–27)

25. **Backups**.
26. **Monitoring**.
27. **Rollout order** — the recommended sequence for production.

## Acceptance

Run the [functional acceptance test](../reference-design/reference/04-technical-reference/08-53-functional-acceptance-test/index.md) at the end of each
milestone, and track progress on the
[Implementation page](../implementation/index.md).