# Phase 17 — Add packwiz CI

Use packwiz as the source-of-truth for the mod list if you want Git review.

Example flow:

```text
pull request modifies pack.toml / index
    ↓
CI validates
    ↓
export Modrinth pack
    ↓
test server starts
    ↓
integration test connects
    ↓
publish runtime revision
```

Keep:

```text
r1
r2
r3
```

for breaking pack changes.

---
