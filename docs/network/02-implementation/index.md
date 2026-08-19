# Part III — Step-by-step implementation

This part is the phased, implementable core. Each numbered page is a deployable increment that proves one contract before moving on.

## Phase roadmap

The source document numbers setup/repository steps as **Phase 0–27** and a separate **rollout order 1–19**. This section preserves the source numbering while grouping into deployable increments.

| Group | Phase | Topic |
|---|---|---|
| **00 Foundations** | — | [Group intro](group-00-foundations.md) |
|  | 00 | Decide names before deploying |
|  | 01 | Create repository structure |
|  | 02 | Create Kubernetes namespaces |
| **01 Core deployment** | — | [Group intro](group-01-core-deployment.md) |
|  | 03 | Deploy CockroachDB and Nakama |
|  | 04 | Deploy Velocity |
|  | 05 | Deploy the Paper lobby |
|  | 06 | Install TAB |
|  | 07 | Add ViaVersion and ViaBackwards |
|  | 08 | Deploy the Forge fantasy runtime |
| **02 Control plane** | — | [Group intro](group-02-control-plane.md) |
|  | 09 | Define the runtime catalog |
|  | 10 | Define map metadata |
|  | 11 | Build the World Controller |
|  | 12 | Build NetworkBridge |
| **03 Product/social** | — | [Group intro](group-03-social.md) |
|  | 13 | Implement friends and parties |
|  | 14 | Implement `/join <friend>` |
|  | 15 | Implement pending cross-runtime invites |
|  | 16 | Publish Modrinth Server Projects |
|  | 17 | Add packwiz CI |
|  | 18 | Add exact world/dimension TAB info |
| **04 Dynamic routing** | — | [Group intro](group-04-dynamic-routing.md) |
|  | 19 | Implement the glitch/random portal |
|  | 20 | Add mc-router |
|  | 21 | Add idle sleep |
|  | 22 | Add Agones for session worlds |
|  | 23 | Add AI proximity chat |
|  | 24 | Community map upload pipeline |
| **05 Operations** | — | [Group intro](group-05-operations.md) |
|  | 25 | Backups |
|  | 26 | Monitoring |
|  | 27 | Rollout order |

## Recommended minimum rollout

For the fastest safe path to a dynamic network, follow the rollout order in `phase-27-rollout-order.md`. That order intentionally proves one contract at a time.