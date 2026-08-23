# Deploy the Forge 1.20.1 fantasy runtime

This runtime is special.

Velocity's current compatibility docs say Forge versions 1.13–1.20.1 are not natively supported by Velocity; use **Ambassador**.

Therefore:

```text
Velocity
  + Ambassador
        ↓
Forge 1.20.1
  + ProxyCompatibleForge
```

ProxyCompatibleForge supplies Velocity modern forwarding support for Forge.

---

## 25.1 Pin the fantasy runtime

Do not use loose ranges.

Record:

```yaml
id: fantasy-1.20.1-forge
minecraft_version: "1.20.1"
loader: forge
loader_version: "PIN_EXACT_TESTED_VERSION"
pack_revision: "r1"
```

Pack revision should change when required client dependencies change.

---

## 25.2 Author the pack

Recommended:

```text
packwiz repository
  ↓ CI export
Modrinth pack/server project
```

packwiz gives you Git-friendly source control.

Modrinth gives players the usable installer/launcher experience.

Use the **AstralRinth** launcher (offline-capable Modrinth App fork) so players on offline/cracked accounts can still receive the required client pack and launch into the runtime.

---

## 25.3 Server installation

Use `itzg/minecraft-server` with the selected modpack installation method.

Mount the world to a PVC.

Do not let the world directory disappear with the Pod.

---

## 25.4 Test proxy switching

Test:

```text
correct fantasy client
lobby -> fantasy
fantasy -> lobby
fantasy backend A -> compatible fantasy backend B
```

Then test wrong runtime:

```text
vanilla client -> fantasy
```

Expected behavior should be a controlled denial/launcher instruction, not a cryptic Forge registry error.

---
