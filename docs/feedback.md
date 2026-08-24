
I unpacked the ZIP and audited the actual `reference-design` tree, then cross-checked the major externally verifiable claims against current official documentation and repositories.

The good news is that the architecture itself has become substantially stronger. The main problem is now **documentation ownership**: the same concepts are explained in several places, while the section that should contain the executable build instructions is mostly empty.

## Main finding: reorganize before adding more information

The ZIP contains **67 Markdown files**. **29 are empty**, and almost all of those empty files are in:

```text
reference-design/
└── 03-step-by-step-implementation/
```

That is the central structural problem.

Parts I, II and IV currently contain implementation-level information because the corresponding Part III files have not been filled in. The result is that a reader learns *why* something exists, then discovers half the installation procedure elsewhere, then encounters schemas in Part IV, while the actual `install-*` page is empty.

I would establish this ownership rule:

```text
PART I
WHY the architecture works this way.
Mental models, product constraints, user experiences.

PART II
WHAT each external tool actually does.
Current verified capabilities and limitations.

PART III
HOW TO BUILD IT.
Commands, manifests, configuration, code, tests.
This should become the largest section.

PART IV
CONTRACTS.
Schemas, state machines, API contracts, invariants, SLOs.

PART V
VERIFICATION.
Current versions, audit date, primary sources, verification status.
```

That is much closer to the structure of your original reference document.

---

# P0 — Fix these technical issues before expanding Part III

There are several things I would correct before using the current design as an implementation specification.

### 1. Fix the Nakama/session design

Modify:

```text
01-understand-the-architecture-before-installing-anything/
social-state-why-nakama-belongs-beside-minecraft-rather-than-inside-it/
index.md
```

Especially:

```text
7.1.0 How an offline/cracked player is authenticated
7.1.1 Linking Minecraft UUID...
7.1.2 Session persistence across launcher restarts
7.1.3 Logout...
```

Your current design says roughly:

```text
OAuth once
→ Nakama returns refresh token
→ NetworkBridge stores it server-side
→ player reconnects
→ NetworkBridge identifies player
→ restores their stored Nakama session
```

The problem is the reconnect proof.

An offline-mode Minecraft UUID/name is spoofable. If NetworkBridge chooses a stored refresh token by looking up that offline identity, the permanent credential may be stored safely server-side, but the **selector used to retrieve it is not authenticated**.

Nakama's current session documentation instead describes storing the session/refresh token in persistent client storage and restoring it when the app starts. ([Heroic Labs][1])

You already have the missing component: **AstralRinth**.

Change the architecture to:

```text
                         FIRST LOGIN
                             │
                             ▼
                   Discord / Google OAuth
                             │
                             ▼
                       Nakama account
                             │
                             ▼
                  AstralRinth stores session
                     in private storage
```

Then reconnect:

```text
AstralRinth
   │
   │ authenticated Nakama session
   ▼
Auth / Join-Ticket Service
   │
   │ returns:
   │ short-lived
   │ single-use
   │ signed ticket
   ▼
Launch Minecraft
   │
   ▼
Velocity
   │
   │ validates + CONSUMES ticket
   ▼
Nakama user established
   │
   ▼
pending invite resolved
```

The crucial distinction becomes:

```text
Offline UUID/name
    = Minecraft presentation identity

Nakama account
    = account identity

Nakama refresh token
    = long-lived credential

Join ticket
    = short-lived proof presented to Velocity

Pending invite
    = user intent, NOT authentication
```

This also gives you exactly the UX you wanted earlier:

```text
Friend invite
→ Install Fantasy
→ Minecraft closes
→ launcher switches runtime
→ Minecraft starts
→ player automatically authenticates
→ pending invite resolves
→ player lands with friend
```

AstralRinth's current README explicitly supports Microsoft, Ely.by, external OAuth Device Authorization and offline accounts for local/testing use. ([GitHub][2])

---

### 2. Correct Nakama's Discord description

Modify the same social-state page and:

```text
02-how-to-interpret-the-actual-tools/
current-verification-notes-2026-08-19/
index.md
```

Currently you say:

```text
authenticateGoogle, or a custom OAuth provider for Discord
```

and:

```text
authenticateCustom (a custom OAuth provider for Discord)
```

That's misleading.

Nakama has an actual Google authentication endpoint. Its documented built-in API exposes Google, Apple, Steam, Facebook, GameCenter, device, email and custom authentication; there is no corresponding native `authenticateDiscord` endpoint. ([Heroic Labs][3])

The accurate design is:

```text
Discord OAuth
    ↓
your Auth service / Nakama beforeAuthenticateCustom hook
    ↓
validate Discord OAuth token / identity
    ↓
obtain stable Discord user ID
    ↓
Nakama AuthenticateCustom
    ↓
Nakama account
```

Nakama explicitly documents this exact third-party pattern: validate the external identity through a `BeforeAuthenticateCustom` hook and map the trusted external user ID into Nakama's custom authentication identity. ([Heroic Labs][4])

So change the terminology from:

> custom OAuth provider

to:

> Discord OAuth is validated by our authentication layer/Nakama runtime hook, then its verified Discord user ID is mapped into Nakama Custom Authentication.

---

### 3. Correct Nakama/PostgreSQL wording

Modify:

```text
01-.../the-selected-tool-stack/index.md
02-.../current-verification-notes-2026-08-19/index.md
```

Current:

```text
PostgreSQL is also supported
```

The situation is awkward because Heroic Labs' comments and formal docs aren't completely aligned.

Current formal Linux documentation says:

* CockroachDB is **officially supported** and optimized;
* PostgreSQL is **unofficially supported for development environments only**. ([Heroic Labs][5])

Current configuration docs simply say Nakama requires a CockroachDB instance. ([Heroic Labs][6])

I would therefore write:

```text
Production database: CockroachDB.

Nakama speaks the PostgreSQL wire protocol and PostgreSQL compatibility
exists, but current formal installation documentation still describes
CockroachDB as the officially supported/optimized production target.
We therefore standardize production on CockroachDB.
```

That removes ambiguity from your implementation guide.

---

# P0 — Fix world lifecycle ownership

### 4. Do not let KEDA and World Controller both own replicas

This affects:

```text
01-.../dynamic-world-lifecycle/index.md
01-.../the-selected-tool-stack/index.md
02-.../capability-cheat-sheet/index.md
03-.../install-keda-and-observability/index.md
03-.../add-idle-sleep/index.md
04-.../recommended-source-of-truth-model/index.md
05-.../final-architecture-recommendation/index.md
```

KEDA can scale an appropriate scale target, and OpenKruiseGame supports GameServerSet scaling. KEDA also supports external scalers. ([KEDA][7])

But your architecture currently gives both:

```text
World Controller
    ↓
GameServerSet.spec.replicas

AND

KEDA/HPA
    ↓
GameServerSet.spec.replicas
```

That creates competing writers.

Explicitly define:

```text
RULE: exactly one replica owner per workload.
```

For your architecture, I recommend:

```text
NAMED PERSISTENT WORLD

MapDefinition
     ↓
World Controller          ← sole replica owner
     ↓
GameServerSet
replicas: 0/1
     ↓
PVC

NO KEDA ScaledObject for this GameServerSet.
```

For a generic pool:

```text
POOLED CAPACITY

KEDA / external scaler    ← sole replica owner
        ↓
GameServerSet
0..N

World Controller allocates/reserves servers,
but DOES NOT patch replicas.
```

This needs to become a formal invariant in Part IV.

Add a glossary entry:

```text
Replica owner
The single controller permitted to mutate the desired replica count
of a workload.
```

---

### 5. Keep OpenKruiseGame — that choice checks out

Don't remove OKG.

The current public release is **OpenKruiseGame v1.1.0**, released June 25, 2026. ([GitHub][8])

Your use of `GameServerSet` is also reasonable. The currently exposed API includes GameServerSet-level game-server templates and PVC-related facilities; OKG remains actively developed. ([GitHub][9])

I would change only this wording:

```text
OpenKruiseGame is a CNCF-incubated workload...
```

to:

```text
OpenKruiseGame is an open-source game-server workload project and
a sub-project of OpenKruise, a CNCF project.
```

That's closer to how the project's own repository describes the relationship. ([GitHub][9])

---

### 6. Qualify `InPlaceIfPossible`

Modify:

```text
01-.../dynamic-world-lifecycle/index.md
01-.../why-several-attractive-projects-are-not-the-foundation/index.md
```

Don't describe it as:

```text
image/config without recreating Pod
```

as a universal property.

Say instead:

```text
OpenKruise can perform supported in-place updates where the changed
pod fields are eligible; unsupported changes fall back to pod recreation.
The world/PVC lifecycle must therefore remain safe under both paths.
```

That prevents someone later assuming an arbitrary Forge config/Java parameter can always be changed without restarting the Minecraft server.

---

# P0 — Fix mc-router semantics

### 7. One Part I page still incorrectly gives mc-router native GameServerSet wake

Modify:

```text
01-understand-the-architecture-before-installing-anything/
why-the-tempting-one-tool-solves-everything-design-is-wrong/
index.md
```

Current:

```text
mc-router can ... wake a Kubernetes GameServerSet
```

Your newer capability table is actually closer to correct.

`mc-router`'s native Kubernetes scale-to-zero support targets StatefulSets. For your OpenKruiseGame architecture, use:

```text
mc-router
   ↓ webhook
World Controller
   ↓
GameServerSet
```

So make that paragraph:

```text
mc-router can detect an incoming hostname connection and initiate
wake-up. Its native Kubernetes scaler is StatefulSet-oriented; in this
architecture an OpenKruiseGame GameServerSet wake is performed through
mc-router's webhook -> World Controller path.
```

This is an important consistency fix because right now Part I and Part II disagree.

---

# P0 — Fix mc-monitor

### 8. Don't call mc-monitor your TPS/performance metrics system

Modify:

```text
01-.../the-selected-tool-stack/index.md
02-.../capability-cheat-sheet/index.md
04-.../world-readiness-contract/index.md
04-.../random-routing-scoring/index.md
05-.../final-architecture-recommendation/index.md
```

You currently say things like:

```text
TPS/latency/ping success (mc-monitor)
```

and:

```text
readiness + perf metrics
```

Split these.

Use:

```text
mc-monitor:
- Minecraft protocol reachability
- status response
- ping/response latency
- current/max online player observation
```

Use another source for:

```text
TPS
MSPT
tick health
heap/GC
entity/chunk cost
```

Prefer:

```text
backend plugin / NetworkBridge metrics
+ spark for diagnostics/profiling
+ Prometheus scrape
```

Then your random scoring becomes:

```text
reachability_factor
    <- mc-monitor

tick_health_factor
    <- backend telemetry

capacity
    <- authoritative NetworkBridge /
       World Controller reservation state
```

That is much cleaner.

---

# P0 — Correct the AstralRinth description

Modify:

```text
01-.../the-selected-tool-stack/index.md
02-.../current-verification-notes-2026-08-19/index.md
05-.../final-architecture-recommendation/index.md
```

Remove:

```text
cracked/pirate-account launcher
primarily aimed at unlicensed play
```

Your own current README doesn't describe the project that way.

It describes AstralRinth as a Modrinth-based launcher supporting Microsoft, Ely.by, external OAuth Device Authorization, and offline accounts for local play/testing, while explicitly encouraging players to own a legitimate Minecraft license. ([GitHub][10])

Use neutral factual wording:

```text
AstralRinth

A 42WASD-tracked Modrinth-based launcher fork with Microsoft,
Ely.by, external OAuth Device Authorization, and offline-account
support.

Role in this architecture:
provide a controllable launcher surface for runtime installation,
account/session handoff, and one-click reconnect.
```

More importantly, change this claim:

```text
It keeps the exact Modrinth App UX...
```

to:

```text
Because AstralRinth is Modrinth-based, Server Project compatibility
is a desired capability, but exact compatibility must be covered by
our launcher acceptance test.
```

I could verify Modrinth Server Projects themselves, but **not** that AstralRinth currently implements every Server Project workflow identically.

Add:

```text
VERIFICATION STATUS: TEST_REQUIRED
```

Modrinth itself absolutely does support the intended flow: a Server Project can define required pack compatibility; its App installs the content and can launch directly into the server. ([Modrinth][11])

---

# P1 — Performance reference needs a fairly major rewrite

Modify:

```text
04-technical-reference/performance-principles/index.md
```

This page currently contains too many Internet-style “Minecraft optimization rules” presented as facts.

Remove or substantially soften:

```text
"#1 cause of MSPT spikes is GC"

"Only use ZGC/Shenandoah with >=6G"

"cores barely matter beyond 4"

"4 CPU is the PaperMC recommendation"

"Paper handles ~100"

"Folia 300–1000+ vs ~150 Paper"

"max-entity-collisions 2"

"villagers 100–200"

"despawn 72"

"simulation-distance 4"

"none change gameplay meaningfully"

ClearLagg / FarmLimiter / VillagerOptimiser as universal recommendations
```

Those are workload-dependent tuning values, not architecture facts.

Paper's current guidance is much simpler: target **20 TPS**, which implies staying below the 50 ms tick budget, and profile your actual workload. Current Paper supports spark directly as its profiling path. ([PaperMC Docs][12])

I would reorganize the page as:

```text
# Performance principles

1. Performance contract
   - target 20 TPS
   - MSPT < 50ms
   - define p95/p99 headroom target

2. Measure before tuning
   - spark
   - backend Prometheus metrics
   - CPU throttling
   - GC
   - disk latency
   - chunk generation

3. JVM
   - start with modern defaults
   - benchmark before adding large flag sets
   - memory limit must include non-heap memory

4. World-generation workload
   - pre-generation where appropriate
   - chunk generation is workload-dependent

5. Entity/simulation workload
   - measure before reducing distances/entity behavior
   - runtime-specific configuration profiles

6. Paper vs Folia
   - Paper default
   - Folia only after workload proves region threading useful
   - every plugin must explicitly support Folia

7. Modded-runtime tuning
   - maintain optimization-mod compatibility matrix
   - benchmark runtime revision, not individual folklore tweaks

8. Capacity testing
   - 10 / 25 / 50 / 100 simulated users
   - record p50/p95/p99 MSPT
   - worldgen on/off
   - party clustering/spread-out cases

9. Performance acceptance criteria
```

Also add the current Java matrix:

```text
Paper 1.20 through 1.21.11 -> Java 21
Paper 26.1+                -> Java 25
Velocity 4.x               -> Java 25
```

Current Paper docs explicitly publish that distinction. ([PaperMC Docs][12])

---

# P1 — Turn MapInstance into an actual Kubernetes resource

Modify:

```text
04-technical-reference/mapinstance-schema/index.md
04-technical-reference/recommended-source-of-truth-model/index.md
```

Right now `MapInstance` is shown as an arbitrary JSON record.

Since you've already chosen a Kubernetes/controller model, make it a real CRD.

For example:

```yaml
apiVersion: platform.42wasd.dev/v1alpha1
kind: MapInstance
metadata:
  name: fantasy-kingdom-001

spec:
  mapRef: fantasy-kingdom
  runtimeRef: fantasy-1-20-1-r4

status:
  phase: Ready

  workloadRef:
    apiVersion: game.kruise.io/v1alpha1
    kind: GameServerSet
    name: fantasy-kingdom-001

  endpoint:
    host: fantasy-kingdom-001.minecraft.svc.cluster.local
    port: 25565

  players: 4
  reservations: 1

  runtimeRevision: r4

  conditions:
    - type: KubernetesReady
      status: "True"

    - type: MinecraftReachable
      status: "True"

    - type: AcceptingPlayers
      status: "True"

  observedGeneration: 12
```

This removes your custom integer:

```text
revision: 14
```

as a home-grown Kubernetes concurrency mechanism where Kubernetes already supplies `resourceVersion`/generation semantics.

Use `status.conditions` rather than adding more and more states later.

---

# P1 — Fix the CRD API group

Modify:

```text
04-technical-reference/recommended-source-of-truth-model/index.md
```

Current:

```text
platform.example/v1
```

Use something real now:

```text
platform.42wasd.dev/v1alpha1
```

And divide ownership:

```text
Git / Argo CD writes:

RuntimeDefinition.spec
MapDefinition.spec
platform deployments
static infrastructure


World Controller writes:

MapInstance
MapInstance.status
dynamic GameServerSets
reservations
runtime operational conditions


Kubernetes / OKG writes:

Pod status
GameServer status
GameServerSet status
PVC state
```

Then write the single-writer rule explicitly.

This is especially important with Argo CD. You don't want:

```text
World Controller -> replicas = 0

two seconds later

Argo CD -> replicas = 1
```

because Git contained `replicas: 1`.

---

# P1 — Separate authentication from invites

Modify:

```text
04-technical-reference/invite-policy/index.md
03-.../implement-pending-cross-runtime-invites/index.md
```

The invite should use the canonical user ID, not the offline Minecraft UUID:

```json
{
  "id": "...",
  "inviter_user_id": "<nakama-user-id>",
  "recipient_user_id": "<nakama-user-id>",

  "mode": "FOLLOW_INVITER",

  "target_runtime_id": null,
  "target_map_id": null,

  "state": "PENDING",

  "expires_at": "..."
}
```

Then define separately:

```text
JoinTicket
```

Example:

```json
{
  "jti": "...",
  "sub": "<nakama-user-id>",
  "aud": "velocity",
  "runtime_id": "fantasy-1.20.1-r4",
  "invite_id": "...",
  "exp": "...",
  "single_use": true
}
```

The invite survives a launcher restart.

The join ticket proves who came back.

Those are not the same thing.

---

# P1 — Strengthen acceptance tests

Modify:

```text
04-technical-reference/functional-acceptance-test/index.md
```

Add:

```text
Authentication

[ ] offline UUID spoof cannot claim another user's Nakama identity
[ ] expired join ticket is rejected
[ ] consumed join ticket cannot be replayed
[ ] changing Minecraft username does not change account identity
[ ] logout invalidates launcher/session continuation
```

Add:

```text
Lifecycle

[ ] GameServerSet 1 -> 0 preserves PVC
[ ] 0 -> 1 mounts same world
[ ] World Controller is sole replica writer for named worlds
[ ] Argo CD does not reset dynamic replicas/status
[ ] KEDA is not attached to a World-Controller-owned GameServerSet
```

Add:

```text
Launcher

[ ] official Modrinth Server Project flow works
[ ] AstralRinth can consume required runtime
[ ] server-project update reaches linked runtime
[ ] pending invite survives restart
[ ] correct account returns after restart
```

And Via needs a compatibility matrix rather than a blanket check because even a current ViaVersion release can contain specific cross-version regressions. The project's own current issue tracker has, for example, a reported 26.2→1.21.11 movement problem on 5.11.0. ([GitHub][13])

---

# P1 — Part III should absorb the missing implementation information

This is the biggest documentation change.

These files currently exist but are empty:

```text
03-step-by-step-implementation/
├── decide-names-before-deploying/
├── create-repository-structure/
├── create-kubernetes-namespaces/
├── install-openkruisegame/
├── install-keda-and-observability/
├── deploy-cockroachdb-and-nakama/
├── deploy-velocity/
├── deploy-the-paper-lobby/
├── install-tab/
├── add-viaversion-and-viabackwards/
├── deploy-the-forge-1-20-1-fantasy-runtime/
├── define-the-runtime-catalog/
├── define-map-metadata/
├── build-the-world-controller/
├── build-networkbridge-for-velocity/
├── implement-friends-and-parties/
├── implement-join-friend/
├── implement-pending-cross-runtime-invites/
├── publish-modrinth-server-projects/
├── add-packwiz-ci/
├── implement-the-glitch-random-portal/
├── add-mc-router/
├── add-idle-sleep/
├── add-ai-proximity-chat/
├── add-object-storage/
├── community-map-upload-pipeline/
├── backups/
├── monitoring/
└── rollout-order/
```

Those pages should contain the material currently scattered elsewhere.

Use exactly the same template for every phase:

```text
# Phase N — Name

## What you are building

## Why this exists

## Prerequisites

## Files you will create/change

## Install

## Configure

## Complete manifest/configuration

## Verify

## Expected output

## Failure cases

## Rollback

## Acceptance criteria

## What becomes true after this phase

## Next phase
```

That consistency will make the documentation feel like the original reference guide again.

---

# Specific moves I would make

### `install-openkruisegame/index.md`

Move/copy implementation detail from:

```text
dynamic-world-lifecycle
the-selected-tool-stack
plain-english-glossary
```

into this page.

It should contain:

```text
OpenKruise prerequisite
OKG v1.1.x
CRDs
GameServerSet example
PVC template
Service
scale 0/1 test
PVC retention test
InPlaceIfPossible caveat
replica ownership invariant
```

OKG v1.1.0 is current and actively released as of June 25, 2026. ([GitHub][8])

---

### `deploy-cockroachdb-and-nakama/index.md`

Move the detailed auth mechanics out of Part I.

Part I should explain:

```text
Nakama is identity/social authority.
```

Part III should explain:

```text
install Cockroach
install Nakama 3.40
configure secrets
configure Custom Authentication hook
Google auth
Discord verification adapter
session lifetimes
launcher/session broker
```

---

### `build-the-world-controller/index.md`

This should become one of the largest pages.

Include:

```text
CRD watches
ensureReady()
single-writer replicas
idempotency
optimistic K8s update
reservations
readiness
route registration
shutdown
conditions
locking/concurrency
```

---

### `build-networkbridge-for-velocity/index.md`

Put here:

```text
Velocity plugin skeleton
Nakama client
join-ticket validation
plugin messaging
presence updates
commands
dynamic server registration
transfer call
MiniPlaceholders
```

Current Velocity 4.x requires Java 25, so that plugin's build/toolchain should also target the currently required Java level. ([PaperMC Docs][14])

---

### `implement-pending-cross-runtime-invites/index.md`

This becomes the canonical explanation of:

```text
invite
→ runtime incompatibility
→ pending intent
→ launcher
→ install/update
→ join ticket
→ relaunch
→ Velocity verification
→ pending intent recovery
→ world wake
→ transfer
```

Part I should only contain the user-facing version.

---

### `add-mc-router/index.md`

Put all of the subtle distinction here:

```text
hostname connection
    ↓
mc-router
    ↓
wake webhook
    ↓
World Controller
```

versus:

```text
already connected player
    ↓
portal
    ↓
World Controller directly
```

---

### `add-idle-sleep/index.md`

Canonicalize:

```text
players == 0
reservations == 0
not maintenance locked
not always_on
not draining already
    ↓
drain
    ↓
save
    ↓
confirm shutdown
    ↓
replicas=0
```

No KEDA on the same named GSS if the World Controller owns its replicas.

---

### `backups/index.md`

Your Velero description currently says:

```text
scheduled PVC snapshots + off-machine copy + restore-test hooks
```

Rewrite more precisely.

Velero can schedule backups and supports resource/volume backup and restore flows; whether a volume is actually durable off-cluster depends on the CSI snapshot/data mover/object-store arrangement. Don't imply “restore testing” is an automatic Velero feature—**restore testing is your runbook/CI process**.

So:

```text
Velero:
Kubernetes resource backup + supported volume backup/snapshot mechanisms
+ backup/restore hooks.

42WASD:
scheduled restore drills + integrity verification.
```

---

# Remove implementation/version facts from the glossary

Your:

```text
plain-english-glossary/index.md
```

is almost 12 KB.

That's too much for a glossary.

A glossary should answer:

> “What does this word mean?”

not:

> “How does the entire architecture implement it?”

Move the essays elsewhere.

Keep entries at roughly 2–8 lines:

```text
Proxy
Backend
Runtime class
MapDefinition
MapInstance
World Controller
GameServerSet
GameServer
PVC
Replica owner
Presence
Reservation
Join ticket
Pending invite
Runtime revision
Protocol translation
Resource pack
Modpack
Scale-to-zero
```

Do not put current versions in the glossary.

---

# Centralize versions instead of repeating them everywhere

Right now things such as:

```text
Velocity 4.0.0
TAB 6.1.2
Via 5.11.0
Nakama 3.40.0
itzg 2026.8.1
```

appear repeatedly.

Create something like:

```text
reference-design/
└── verified-versions.yaml
```

Example:

```yaml
audit_date: "2026-08-24"

components:
  velocity:
    version: "4.0.0"
    java: 25

  tab:
    version: "6.1.2"

  viaversion:
    version: "5.11.0"

  viabackwards:
    version: "5.11.0"

  nakama:
    version: "3.40.0"

  openkruisegame:
    version: "1.1.0"

  minecraft_server_image:
    version: "2026.8.1"

  cloudnet:
    version: "4.0.0-RC17"
    status: "pre-release"

  shulker:
    version: "0.13.0"
    status: "maintenance-risk"
```

For example, current CloudNet 4 development is still RC-based; RC17 was announced August 9, 2026. ([GitHub][15]) Shulker's latest visible release remains v0.13.0 from April 5, 2025. ([GitHub][16])

Then documentation says:

```text
See verified-versions.yaml.
```

instead of hard-coding versions in ten pages.

---

# I would also change Part V

Currently:

```text
05-current-verification-references/
```

is basically a source list.

Make it an **audit table**:

| Component                | Current status | Architecture status | Verified claim                                                   | Last checked |
| ------------------------ | -------------- | ------------------- | ---------------------------------------------------------------- | ------------ |
| Velocity                 | active         | SELECTED            | Java 25 / Forge rules                                            | 2026-08-24   |
| Gate                     | active         | ALTERNATIVE         | ViaLite + mod relay                                              | 2026-08-24   |
| OKG                      | v1.1.0         | SELECTED            | GSS / game workload                                              | 2026-08-24   |
| TAB                      | 6.1.2          | SELECTED            | Velocity/MiniPlaceholders                                        | 2026-08-24   |
| ViaVersion               | 5.11.0         | SELECTED            | protocol translation                                             | 2026-08-24   |
| Nakama                   | 3.40.0         | SELECTED            | social/auth/session                                              | 2026-08-24   |
| Modrinth Server Projects | active         | SELECTED            | install + direct launch                                          | 2026-08-24   |
| AstralRinth              | active fork    | SELECTED/TEST       | launcher basics verified; Server Projects integration unverified | 2026-08-24   |
| Shulker                  | v0.13.0 / 2025 | REJECTED            | maintenance concern                                              | 2026-08-24   |
| CloudNet                 | 4.0 RC         | ALTERNATIVE         | Minecraft-native cloud                                           | 2026-08-24   |

That transforms Part V into something you can **re-audit mechanically**.

---

## What I would keep

A lot of your conceptual work is good and should survive mostly intact.

Keep:

```text
the-one-sentence-idea
the-complete-mental-model-seven-separate-layers
runtime-classes-the-rule-that-makes-seamless-ux-possible
proxy-decision-velocity-vs-gate...
end-to-end-user-experiences
routing-state-machine
why-this-architecture-is-intentionally-not-fully-automatic...
```

The runtime-class rule remains particularly important.

Velocity is also still the sensible default. Current Paper docs confirm the Forge split you're using: modern Forge >1.20.2 has native Velocity support, while Forge 1.13–1.20.1 needs Ambassador, and modern forwarding on Forge needs ProxyCompatibleForge/SpongeForge. ([PaperMC Docs][17])

TAB 6.1.2 and ViaVersion/ViaBackwards 5.11.0 are also still current choices. ([GitHub][18])

And Modrinth Server Projects remain one of the strongest pieces of this entire design: Modrinth explicitly built them around required modpack installation, linked server instances, automatic compatibility updates and direct server launch. ([Modrinth][11])

## Overall verdict

I would **not redesign the platform again**.

The architecture has converged reasonably well around:

```text
Velocity
+
NetworkBridge
+
Nakama / CockroachDB
+
World Controller
+
OpenKruiseGame
+
runtime classes
+
Modrinth/AstralRinth client management
```

The next major work should be documentation consolidation, not another stack search.

The biggest immediate changes are:

1. **Fill Part III.**
2. **Fix the reconnect authentication model with launcher-held credentials + one-time join tickets.**
3. **Make World Controller the sole replica owner for named persistent worlds.**
4. **Correct mc-monitor/mc-router/KEDA boundaries.**
5. **Turn MapInstance/MapDefinition/RuntimeDefinition into coherent CRD contracts.**
6. **Reduce Part I to concepts and Part IV to contracts.**
7. **Centralize current versions and verification status.**

I completed the ZIP inventory and a broad/current web re-audit of the architecture's major external components and the highest-risk claims. I did **not** finish a literal sentence-by-sentence web verification of every factual sentence in all 38 non-empty Markdown files before this response; in particular, the long performance page contains numerous individual plugin/mod tuning claims that should be reworked around benchmarking rather than preserved and individually “certified.” The issues above are the ones I would address before writing the missing implementation chapters.

[1]: https://heroiclabs.com/docs/nakama/concepts/session/?utm_source=chatgpt.com
[2]: https://github.com/42WASD/AstralRinth?utm_source=chatgpt.com
[3]: https://heroiclabs.com/docs/nakama/concepts/authentication/?utm_source=chatgpt.com
[4]: https://heroiclabs.com/docs/nakama/guides/concepts/custom-authentication/?utm_source=chatgpt.com
[5]: https://heroiclabs.com/docs/nakama/getting-started/install/linux/?utm_source=chatgpt.com
[6]: https://heroiclabs.com/docs/nakama/getting-started/configuration/?utm_source=chatgpt.com
[7]: https://keda.sh/docs/2.21/scalers/external/?utm_source=chatgpt.com
[8]: https://github.com/openkruise/kruise-game/releases?utm_source=chatgpt.com
[9]: https://github.com/openkruise/kruise-game?utm_source=chatgpt.com
[10]: https://github.com/42WASD/AstralRinth
[11]: https://modrinth.com/news/article/introducing-server-projects/?utm_source=chatgpt.com
[12]: https://docs.papermc.io/paper/getting-started/?utm_source=chatgpt.com
[13]: https://github.com/ViaVersion/ViaVersion/issues/5015?utm_source=chatgpt.com
[14]: https://docs.papermc.io/velocity/faq/?utm_source=chatgpt.com
[15]: https://github.com/CloudNetService/CloudNet/discussions/categories/releases?utm_source=chatgpt.com
[16]: https://github.com/jeremylvln/Shulker/releases?utm_source=chatgpt.com
[17]: https://docs.papermc.io/velocity/server-compatibility/?utm_source=chatgpt.com
[18]: https://github.com/NEZNAMY/TAB/releases?after=2.8.11-pre15&utm_source=chatgpt.com
