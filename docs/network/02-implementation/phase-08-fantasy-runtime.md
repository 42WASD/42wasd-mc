# Phase 8 — Deploy the Forge 1.20.1 fantasy runtime

This runtime is special. Velocity's current compatibility docs say Forge versions 1.13–1.20.1 are not natively supported by Velocity; use **Ambassador**.

```text
Velocity + Ambassador
        ↓
Forge 1.20.1 + ProxyCompatibleForge
```

ProxyCompatibleForge supplies Velocity modern forwarding support for Forge.

## Pin the fantasy runtime

Do not use loose ranges. Record:

```yaml
id: fantasy-1.20.1-forge
minecraft_version: "1.20.1"
loader: forge
loader_version: "PIN_EXACT_TESTED_VERSION"
pack_revision: "r1"
```

The pack revision should change when required client dependencies change.

## Author the pack

```text
packwiz repository → CI export → Modrinth pack/server project
```

packwiz gives you Git-friendly source control. Modrinth gives players the usable installer/launcher experience.

## Server installation

Use `itzg/minecraft-server` with the selected modpack installation method. Mount the world to a PVC. Do not let the world directory disappear with the Pod.

## Test proxy switching

Test:

```text
correct fantasy client
lobby -> fantasy
fantasy -> lobby
fantasy backend A -> compatible fantasy backend B
```

Then test the wrong runtime:

```text
vanilla client -> fantasy
```

Expected behavior should be a controlled denial/launcher instruction, not a cryptic Forge registry error.