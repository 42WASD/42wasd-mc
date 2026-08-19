# Group 01 — Core deployment

These phases stand up the foundation runtime: the database + social backend, the public proxy, the Paper lobby, TAB, protocol translation, and the modded fantasy runtime.

- **[Phase 3 — Deploy CockroachDB and Nakama](phase-03-nakama.md)** — production social backend.
- **[Phase 4 — Deploy Velocity](phase-04-velocity.md)** — the public proxy.
- **[Phase 5 — Deploy the Paper lobby](phase-05-lobby.md)** — the first backend.
- **[Phase 6 — Install TAB](phase-06-tab.md)** — global player display.
- **[Phase 7 — Add ViaVersion and ViaBackwards](phase-07-protocol.md)** — protocol translation.
- **[Phase 8 — Deploy the Forge fantasy runtime](phase-08-fantasy-runtime.md)** — the modded runtime.

**Gate:** at the end of this group you have a working proxy with a lobby, identity-preserving forwarding, global TAB, protocol translation, and a separate fantasy runtime.

> **Rollout mapping:** steps **1–4** of the rollout order (Velocity + lobby, secure forwarding, TAB, ViaVersion/Backwards test) live here. Phase 3 (Nakama identity) is step **5**.