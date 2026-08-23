# The complete mental model: seven separate layers

## 2.1 ENTRY — “How does the player reach the network?”

Recommended:

```text
Internet
   ↓
mc-router (optional)
   ↓
Velocity
```

Use `mc-router` when hostname routing and edge-triggered wake-up are useful.

Examples:

```text
play.example.com
survival.example.com
map-abc.example.com
```

If every player always enters through one address and all routing happens after login, `mc-router` is optional.

---

## 2.2 PROXY — “Which backend should this connected player use?”

Recommended default: **Velocity**.

Responsibilities:

```text
Mojang authentication
backend connection switching
proxy commands
TAB plugin
ViaVersion/ViaBackwards
Forge compatibility bridge
NetworkBridge
```

Velocity is the selected default because this architecture values the **usable Minecraft plugin ecosystem** more than minimizing proxy process size.

---

## 2.3 SOCIAL — “Who is friends with whom, who invited whom, and what are they doing?”

Recommended: **Nakama**.

Responsibilities:

```text
Minecraft UUID -> network account mapping
friends
friend requests
parties
party invites
presence/status
notifications
pending cross-runtime join
optional matchmaking/listing logic
```

Do not force a Minecraft proxy plugin to become your entire social backend.

---

## 2.4 WORLD CONTROL — “Which world instance exists, and is it ready?”

Recommended: a **small custom World Controller service**.

Responsibilities:

```text
map catalog
runtime compatibility
instance lifecycle
Kubernetes scale 0 -> 1
readiness checks
capacity reservations
random-map selection
route registration
idle scale-down policy
```

This service should have narrowly scoped Kubernetes permissions.

---

## 2.5 GAME SERVERS — “Where does simulation actually run?”

Recommended container foundation:

**`itzg/minecraft-server`**

Use:

```text
Paper for vanilla-compatible modes
Forge for fantasy-1.20.1
persistent StatefulSet + PVC for durable worlds
Agones only for session-style disposable/warm-pool instances
```

---

## 2.6 PROTOCOL — “Can this Minecraft protocol version communicate?”

Recommended on Velocity:

```text
ViaVersion
ViaBackwards
```

Use protocol translation only for runtime classes designed to tolerate version translation.

Do not treat it as a substitute for mod compatibility testing.

---

## 2.7 CLIENT RUNTIME — “Does the player have the required game + loader + mods?”

Recommended public onboarding:

**Modrinth Server Projects**

Recommended pack authoring/CI option:

**packwiz**

The launcher layer owns:

```text
Minecraft version
loader
required mods
mod versions
configs
resource packs
runtime updates
```

---
