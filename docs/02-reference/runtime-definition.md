# RuntimeDefinition schema

A **runtime class** is the single source of truth for "what client set / server backend is required to play a given map." The core rule: *a community map may be dynamic, but the required client runtime must be standardized.*

## Fields

```yaml
runtimeId: string          # e.g. vanilla-current, backrooms-current, fantasy-1.20.1-forge, experimental-*
kind: string               # the runtime kind, e.g. "paper", "forge", "vanilla"
minecraftVersion: string   # e.g. "1.20.1", "current"
loader:
  type: string             # none | forge | fabric | ...
  version: string
image:
  reference: string        # container image + tag/digest
  java: string             # e.g. "25" for Velocity, "21" for Paper, etc.
modpack:
  type: string             # modrinth | packwiz | none
  projectId: string        # Modrinth project id when applicable
compatibleClients: []      # list of client runtime classes that may join
forwarding:
  mode: string             # modern | legacy | none
  needsAmbassador: bool    # true for Forge runtimes (ProxyCompatibleForge)
```

## Example

```yaml
runtimeId: fantasy-1.20.1-forge
kind: forge
minecraftVersion: 1.20.1
game:
  type: forge
  version: "47.3.0"
image:
  reference: itzg/minecraft-server:2026.8.0
  java: "21"
protocol:
  projectId: "fantasy-project-123"
  packwiz: false
compatibleClients: [fantasy-1.20.1-forge]
forwardedProtocol:
  mode: modern
  needsAmbassador: true
```

## Rules

- **Standardize the required runtime** — a map does not get a bespoke runtime.
- A runtime has exactly one `runtimeId` (stable identifier).
- `compatibleClients` drives routing compatibility (Steps 12, 15).

## See also

- [Understanding: runtime classes](../00-understand/04-runtime-classes.md)
- [Step 13 — Fantasy Forge](../01-implement/step-13-fantasy-forge.md)