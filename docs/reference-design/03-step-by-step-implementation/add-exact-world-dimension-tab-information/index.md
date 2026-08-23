# Add exact world/dimension TAB information

To show the player's **current dimension** (Overworld / The Nether / Level 0)
in TAB you need two pieces of code talking to each other:

- a **backend-side bridge** (a small plugin/mod on each runtime) that observes
  dimension/world changes for its connected players and pushes them out, and
- the **proxy-side NetworkBridge** (Velocity plugin) that receives those
  events, updates presence in Nakama, and exposes the values to TAB.

The backend bridge is the part that knows the truth — only the backend actually
sees a player change dimension (through a portal or teleport). The proxy cannot
infer it from the server name, so the backend must report it.

## Use the standard transport: plugin messaging

You do **not** need a bespoke wire protocol. The backend→proxy channel is the
Minecraft **plugin-messaging** mechanism (the BungeeCord plugin-messaging
channel, which Velocity supports natively): a backend plugin calls
`player.sendPluginMessage(...)` and the proxy plugin receives it. NetworkBridge
registers the channel and handles the inbound event. This is the same mechanism
used by BungeeCord/Velocity plugin-bridge plugins (e.g. TAB-Bridge,
PAPIProxyBridge) to forward backend data to the proxy.

The only genuinely custom part is a thin **dimension-watch** plugin per runtime:
on Paper/Forge it listens for a dimension/teleport event and emits a plugin
message. There is no turnkey plugin that does this generically for arbitrary
modded dimension names, so a small bridge is still required — but the transport
itself is standard.

## Backend-side presence bridge

On each runtime/backend that must show exact dimension, install a thin bridge
plugin/mod (one per runtime family). Its job:

```text
listen for player dimension change (world/player teleport / respawn)
   ↓
build the change event (below)
   ↓
sendPluginMessage to the proxy (NetworkBridge) over a custom channel
```

It must be keyed by the **Minecraft UUID** so the proxy/Nakama can attribute it
to the right Nakama account. Do not key by username (usernames can change).

The backend bridge sends world change:

```json
{
  "player_uuid": "...",
  "runtime_id": "vanilla-current",
  "map_id": "survival-main",
  "dimension": "minecraft:the_nether"
}
```

The backend knows `map_id`/`runtime_id` from its own config; it reads
`dimension` from the player's current world/dimension (Minecraft namespaces
like `minecraft:overworld`, `minecraft:the_nether`, or custom mod dimensions).

## Proxy-side handling

NetworkBridge receives the plugin message, updates presence, then exposes:

```text
<network_map>
<network_runtime>
<network_dimension>
```

TAB then displays:

```text
Fantasy Kingdom
  Ahmad — Overworld
  Alex  — The Nether

Backrooms
  Steve — Level 0
```

Do not infer dimension from proxy server name.

> **Note — two components required.** This page assumes both the backend bridge
> and the NetworkBridge side exist. The NetworkBridge side is built in
> `build-networkbridge-for-velocity`; the backend bridge is a per-runtime
> plugin/mod you add here. Without it, exact dimension data never reaches TAB.

---
