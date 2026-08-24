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
Minecraft **plugin-messaging** mechanism: a backend plugin calls
`player.sendPluginMessage(...)` on a **dedicated channel** (e.g. `42wasd:presence`)
and the proxy plugin receives it. NetworkBridge registers the channel and
handles the inbound event.

## Backend-side presence bridge

On each runtime/backend that must show exact dimension, install a thin bridge
plugin/mod (one per runtime family). Its job:

```text
listen for player dimension change (world/player teleport / respawn)
   ↓
build the change event (below)
   ↓
sendPluginMessage to the proxy (NetworkBridge) over the 42wasd:presence channel
```

It must be keyed by the **Minecraft UUID** so the proxy/Nakama can attribute it
to the right Nakama account. Do not key by username (usernames can change).

The backend bridge sends a world-change event:

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

### Security: mark the channel handled, trust only backend sources

Velocity's plugin-messaging docs warn that a handler must mark matching
messages `handled()` **before** running source logic; otherwise the message can
be forwarded and a malicious client can impersonate the proxy/backend messaging
layer. The proxy handler should look like this:

```java
if (!"42wasd:presence".equals(event.getIdentifier().getId())) {
    return; // not ours; leave default forwarding behavior
}

// Stop the message from being forwarded anywhere else.
event.setResult(PluginMessageEvent.ForwardResult.handled());

// Only trust messages that came from an actual backend server connection,
// never from a player/client.
if (!(event.getSource() instanceof ServerConnection backend)) {
    return;
}

// Now parse the authenticated backend-origin payload.
PresenceUpdate update = parse(event.getData());
```

Also do **not** blindly trust the `player_uuid` in the payload:

```json
{
  "player_uuid": "..."
}
```

Cross-check that the claimed player actually belongs to that backend
connection / the current backend state before updating presence for them.
Treat any payload that does not come from a known backend connection as
untrusted.

> **Note — two components required.** This page assumes both the backend bridge
> and the NetworkBridge side exist. The NetworkBridge side is built in
> `build-networkbridge-for-velocity`; the backend bridge is a per-runtime
> plugin/mod you add here. Without it, exact dimension data never reaches TAB.

---
