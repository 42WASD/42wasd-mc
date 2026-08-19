# Step 14 — Modrinth Server Project

Define the fantasy runtime's client+server modpack as a **Modrinth Server Project**, so the runtime (which mods a client needs) is versioned, resolvable, and reusable — including across new map uploads.

## Goal

The `fantasy-1.20.1-forge` runtime's modset is captured as a Modrinth Server Project that a client references to join, and that future maps can build on.

## Tasks

### 1. Create the Server Project

- Publish a Modrinth Server Project (or a versioned project file) describing the Forge + mods for `fantasy-1.20.1-forge`.
- Include the Forge version, loader, and exact mod versions in the metadata.

### 2. Tie the runtime to the project

- In the controller's `RuntimeDefinition`, reference the Modrinth project/version for `fantasy-1.20.1-forge`.
- This is how a client knows which modpack to install and which server it's allowed to join.

### 3. Add/verify on the server

- The server side should consume the same project (or a server-compatible variant) so client and server agree on the runtime.

## Acceptance criteria

```text
[ ] `fantasy-1.20.1-forge` has a resolvable Modrinth project/version
[ ] client runtime matches the Modrinth-defined set
[ ] new fantasy maps use the same runtime project
[ ] version bumps to the project are tracked/documented
```

## Next step

[Step 15 — Cross-runtime invite](step-15-cross-runtime-invite.md)