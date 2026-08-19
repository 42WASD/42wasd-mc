# Step 4 — ViaVersion / ViaBackwards

Let clients on a different protocol version connect, and let the proxy handle cross-version translation between the proxy and backends.

## Goal

A client running an older/newer protocol than the backends can still join and play.

## Tasks

### 1. Decide where translation happens

Two common approaches:

- **Proxy-level** — ViaVersion on Velocity translates for all backends. Simple, one place to configure, but all backends must present a consistent protocol to the proxy.
- **Backend-level** — ViaVersion on each backend. Needed when backends run different runtime classes (Step 13, Fantasy Forge on 1.20.1) and each exposes its own protocol.

Plan for **backend-level** translation per runtime, since Step 13 introduces a different Minecraft version runtime.

### 2. Install on each backend

Add ViaVersion and ViaBackwards to each backend's `plugins/`.

```text
ViaVersion-5.11.0.jar
ViaBackwards-5.11.0.jar
```

### 3. Verify translation

Join with a client of an older protocol version and confirm you can enter the lobby and move.

## Acceptance criteria

```text
[ ] older-version client joins through the proxy
[ ] player reaches the backend without a protocol error
[ ] plugin order is stable across restarts
[ ] document the target protocol version per backend
```

## Relationship to runtime classes

The **required client runtime is standardized** even though map content may be dynamic. ViaVersion handles *protocol* drift; runtime class still decides which backend a client is allowed to join (Step 13).

## Next step

[Step 5 — Nakama identity mapping](step-05-nakama-identity.md)