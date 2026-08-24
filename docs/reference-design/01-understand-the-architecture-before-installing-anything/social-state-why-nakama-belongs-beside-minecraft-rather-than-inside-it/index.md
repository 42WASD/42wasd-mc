# Social state: why Nakama belongs beside Minecraft rather than inside it

A proxy plugin can implement `/friend`, `/party`, and `/invite`.

The question is whether it should become the **authoritative database and realtime social system**.

Nakama already has the game-backend primitives:

```text
authentication identity
friends
parties
party invites
presence/status
notifications
chat
match/listing/matchmaking primitives
server runtime functions
```

Use Minecraft as one client/frontend of that social system.

> **What "use Minecraft as one client/frontend" means:** the Nakama backend is
> the owner of identity, friends, parties and presence; the Minecraft client
> (through Velocity/NetworkBridge) is just one *client* that reads/writes that
> social state. The same social backend could equally serve a website, a mobile
> app, or a Discord bot. Minecraft is not the database — it is the frontend.
> In particular, login happens **server-side at the proxy gate** (via the
> Velocity auth plugin), not in a built-in Minecraft login page. The Minecraft
> client does not render HTML and has no custom-network account UI, so all
> OAuth/login/logout UI is provided by NetworkBridge + Nakama (in-game
> prompts/commands and a browser for the OAuth consent).

---

## 7.1 Identity mapping

The canonical identity is the **Nakama user account, created via OAuth-first
social authentication** (Discord and/or Google). Minecraft identity is a linked,
secondary attribute — never the identity anchor.

Why OAuth-first: this network permits offline/cracked accounts behind the
authenticated proxy (see Phase 6). An offline-mode Minecraft UUID is generated
from the username and is spoofable — anyone can join with any name, so it
cannot be trusted as a canonical identity. A Discord/Google OAuth token proves
who the player is, prevents impersonation, and makes bans attach to a real,
verified account.

Example:

```text
Discord / Google OAuth token
       ↓
Nakama social-provider authentication (authenticateGoogle, or a custom OAuth
                                        provider for Discord)
       ↓
nakama_user_id  (canonical identity)
       ↓
linked Minecraft identity (per-lookup, see below)
```

Maintain a table/mapping such as:

```json
{
  "nakama_user_id": "....",
  "discord_id": "...",          // or google_id, if chosen
  "minecraft_uuid": "123e4567-e89b-12d3-a456-426614174000",
  "minecraft_name": "Steve"
}
```

The Minecraft UUID/name here are **runtime/presentation bindings** for the
current session, not the security anchor. They must be re-derived from the
verified Nakama session, never trusted from the offline client alone.

Do not make usernames authoritative; usernames can change.

### 7.1.0 How an offline/cracked player is authenticated (in-game auth gate)

The apparent contradiction is: *this network permits offline/cracked accounts,
but identity is OAuth-first (Discord/Google). How does a cracked player get an
OAuth token?*

The answer is an **in-game authentication gate**, not a launcher-side handoff.
The player connects to the network with any (even unverified) Minecraft client
and lands on a **login/gate stage**; they authenticate and link their account
**there, after joining**, before they are allowed into any real world. This is
the standard proxy pattern — e.g. a Velocity auth gate (VeloAuth) that blocks
transfers until "you must link your Discord account to play", or an in-game
registration/login plugin that drops new players on the lobby until they
`/register` / `/login`.

```text
1. Player joins the network (any offline/cracked client)
   ↓
2. Velocity routes them to the gate stage (a login lobby), NOT to a world
   ↓
3. NetworkBridge prompts: "Sign in with Google / Discord"
   (a one-time network account creation / login — NOT Mojang)
   ↓
4. Player completes the OAuth flow (browser or in-game prompt)
   ↓
5. Nakama verifies the token and creates/returns the canonical
   Nakama user account (authenticateGoogle / custom Discord provider)
   ↓
6. NetworkBridge links the incoming (offline) Minecraft UUID/name to the
   verified account (Nakama account.link/custom)
   ↓
7. Only now is the player routed from the gate to the lobby/world
```

So the OAuth happens **server-side in the gate**, not in the launcher and not
before join. Offline/cracked clients can reach the network because the backend
worlds run offline-mode behind the proxy — but they cannot leave the gate until
they authenticate. The gate is what makes the offline network safe: a username
alone grants nothing until a verified Nakama account is linked to it.

For a player with a legit Microsoft/Mojang account, the flow is the same —
they are **not** asked for a Microsoft login on the server side. The network
never trusts the Mojang session to *authorize* anything; it only uses the
Nakama session as the canonical identity and treats the Minecraft UUID/name as
a linked, per-session runtime binding. So "cracked vs premium" changes *which
client* reaches the gate, not *whether* identity exists — both paths converge
on the same Nakama OAuth session at the gate.

> **Premium-player note:** a legitimate Mojang player is already signed into
> Microsoft in their client, but that does **not** skip our gate. They still
> complete the one-time Nakama sign-up/login (Discord or Google) exactly once,
> because the network treats the Nakama account — not the Mojang session — as
> the identity anchor. This is a one-time friction for every user (premium and
> cracked alike); it is not a recurring login. Do not market this as
> "no login needed" — everyone registers/linked their network account once.

This is why the auth gate is a required part of the proxy (NetworkBridge +
Nakama), not an optional convenience: without it, an offline/cracked client
could reach a world with no verified identity at all.

### 7.1.1 Linking Minecraft UUID to the OAuth account

Because the backends run in offline mode, the proxy (Velocity NetworkBridge)
is the only party that sees both the OAuth-verified Nakama account and the
incoming Minecraft connection. It must bind them server-side:

```text
player joins Velocity
   ↓
NetworkBridge authenticates to Nakama with OAuth-verified session
   ↓
NetworkBridge links the incoming offline UUID/name to that Nakama account
      (Nakama account.link/custom, scoped to that session)
   ↓
backend sees the UUID the bridge assigned
```

The bridge, not the offline client, is the trusted source for the
UUID->Nakama mapping.

### 7.1.2 Session persistence across launcher restarts

A player must **not** re-gate every time they restart the launcher to switch
runtimes. The Nakama OAuth session survives a reconnect:

```text
player authenticates once at the gate
   ↓
Nakama returns a session token + refresh token
   ↓
NetworkBridge persists the session (Nakama session/refresh tokens) keyed to
   the linked account (server-side, in Nakama / CockroachDB)
   ↓
player restarts the launcher to switch runtimes
   ↓
reconnect: NetworkBridge restores/renews the Nakama session from the refresh
   token — no new Discord/Google prompt
   ↓
player is routed onward immediately
```

Mechanics, per Nakama's session model:

- The Nakama **access token** is short-lived; the **refresh token** is
  long-lived and lets the server renew the session without re-authenticating.
- On a fresh join the bridge restores the session to the *same* Nakama account
  by presenting the stored **refresh token** (a bearer secret scoped to that
  account), not by re-running the Discord/Google OAuth. The offline Minecraft
  UUID/name alone is **never** enough to claim a session — the refresh token
  is the credential that binds the reconnect to the account, so a spoofed UUID
  cannot hijack a stored session without that token.
- Only when the **refresh token also expires** (or the player explicitly signs
  out) does the player go back through the gate.

This is what makes the "seamless" cross-runtime invite (Example D) hold: the
launcher restart to install a new runtime does **not** force a re-login,
because the Nakama session persists. Document this explicitly so the auth gate
("sign in before transfer") is understood to be *one-time*, not *per-join*.

### 7.1.3 Logout and switching accounts

Because the session is durable, you must provide an explicit escape hatch so a
player can end it or sign in as someone else. NetworkBridge should expose a
**logout / switch-account command** (e.g. `/logout` or `/switch-account`):

```text
/logout
   ↓
NetworkBridge tells Nakama to revoke/expire the session (revoke the refresh token)
   ↓
player is dropped back to the gate stage
   ↓
on next join, the gate prompts for Discord/Google sign-in again
```

- **`/logout`** revokes the stored refresh token server-side, so the next join
  cannot silently reuse it. The player must complete the OAuth gate again.
- **Switch account** = logout, then re-auth as a different Discord/Google
  account. The new Nakama account becomes the canonical identity; the offline
  Minecraft UUID/name is re-linked to it. This is how a shared machine or a
  user with multiple social accounts switches cleanly without the old session
  leaking.
- The **same logout command works for cracked and premium players** — both are
  just Nakama sessions, so signing out is identical.

This keeps the auth gate *one-time-per-session* while still allowing a player
to explicitly end or change their identity. The logout/switch command is part
of NetworkBridge's command set, not a Minecraft-client feature (the Minecraft
client has no built-in HTML or account-switch UI for a custom network — all of
this happens through the proxy/bridge).

### 7.1.4 One account, multiple characters (Terraria-style)

The canonical identity is the **Nakama account**. A common game pattern is for
one account to own **multiple in-world characters** — like Terraria, where one
player account can create several named characters that each have their own
inventory/progress.

- The Nakama **account** is the security + ownership anchor (bans, purchases,
  friends, login). It is identified by `nakama_user_id`.
- **Characters** are a layer above the account, *not* Nakama users. They are
  records owned by the account — naturally a Nakama **collection** (one record
  per character) keyed by the account, plus an `active_character_id` pointer.
- The **offline Minecraft UUID/name** becomes the *character's* presentation
  identity, bound to the character record — so even if a player uses a
  different username, or another person on a shared machine, the data and
  inventory resolve to the same **account + character**, never to the raw
  username. Two different usernames can no longer collide into the same world
  data, and a username change does not lose the character.

```text
Discord/Google account  (nakama_user_id = stable identity anchor)
        │  owns
        ├── character "Steve"    (minecraft_uuid/name, inventory, settings)
        ├── character "Pixel"     (a second, separate character)
        └── active_character = "Steve"
```

- **Friends/parties attach to the account**, and the *active* character
  determines what appears in the world and in TAB. When the player switches
  character, their presence `activity`/`map` reflects the new character.
- This is a **data/collection design on top of Nakama**, not a Nakama
  feature. It is the established pattern: one authenticated user, with
  per-account child records for characters/profiles. It decouples "who owns
  the account" from "which character is in the world," which is exactly what
  prevents two players with the same username from accidentally sharing a
  character.

---

## 7.2 The Minecraft client does not need a Nakama SDK

The flow can remain fully server-side:

```text
Minecraft client
    ↓
Velocity NetworkBridge
    ↓
Nakama HTTP / realtime API
```

The proxy acts as a trusted broker.

That means ordinary vanilla clients do not install anything merely to use:

```text
/friend
/party
/invite
/join
/worlds
/random
```

---

## 7.3 Presence model

A useful status object:

```json
{
  "runtime_id": "backrooms-current",
  "map_id": "backrooms-level-0-a17",
  "backend_id": "map-a17",
  "dimension": "minecraft:overworld",
  "activity": "exploring",
  "joinable": true,
  "party_id": "optional"
}
```

This one object can power:

```text
TAB
/join <friend>
friend menu
invite routing
party-follow
web status page
```

### 7.3.1 Presence source of truth

Two systems look like they could own "where is the player / what world":

- **Nakama** — owns the *social/presence* graph (who is online, friends,
  parties, invites). This is the object's owner and the answer to
  "who is where, socially".
- **World Controller** — owns the *operational* world facts (is this
  `MapInstance` READY/ASLEEP, what's the service endpoint, capacity,
  reservations). This is the source for "can a world accept a transfer".

The split is by *kind of truth*:

```text
Nakama presence      = the player's social view (who/where among friends)
World Controller     = the world's operational truth (READY/ASLEEP, capacity,
                       routing-eligibility)
```

- **Presence (the object above) is owned by Nakama.** The backend/bridge
  reports runtime/map/dimension *changes* to Nakama (through NetworkBridge),
  and Nakama is the authority for `/join`, friend lists, and the web status
  page. TAB reads presence from Nakama.
- **Operational readiness is owned by the World Controller.** It is the only
  source for `MapInstance.state`, capacity, and reservations, because only it
  can wake a sleeping world or know whether a transfer can land.

So: **Nakama is the source of truth for *presence*; the World Controller is
the source of truth for *operational world state*.** They agree on `map_id`
and `runtime_id`; they never double-author the same fact. When NetworkBridge
resolves a `/join`, it asks the World Controller for operational readiness and
Nakama for the friend's current presence, then reconciles the two.

---
