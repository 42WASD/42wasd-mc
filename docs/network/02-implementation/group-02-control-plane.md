# Group 02 — Control Plane

These phases build the custom control plane: the runtime catalog, map metadata, the World Controller, and the NetworkBridge plugin.

- **[Phase 9 — Define the runtime catalog](phase-09-runtime-catalog.md)**
- **[Phase 10 — Define map metadata](phase-10-map-metadata.md)**
- **[Phase 11 — Build the World Controller](phase-11-world-controller.md)**
- **[Phase 12 — Build NetworkBridge](phase-12-network-bridge.md)**

**Gate:** at the end of this group, the network can wake/register/route worlds and the proxy can call the control plane safely (no admin kubeconfig in the plugin).

> **Rollout mapping:** steps **8–10** of the rollout order (World Controller, scale-to-zero map, portal wake → transfer). The narrower scoped World Controller is the heart of dynamic routing.