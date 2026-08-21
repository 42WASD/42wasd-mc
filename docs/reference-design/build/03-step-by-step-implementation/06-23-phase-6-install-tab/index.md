# Phase 6 — Install TAB

Use current stable TAB release.

At audit time:

```text
TAB 6.1.2
```

Install TAB on Velocity.

Start with server-level display:

```text
Lobby
  Steve
  Alex

Survival
  Ahmad
```

Do not attempt exact dimensions yet.

---

## 23.1 Add MiniPlaceholders if needed

TAB on Velocity can integrate with MiniPlaceholders.

Later your NetworkBridge can expose values such as:

```text
<network_runtime>
<network_map>
<network_dimension>
<network_party>
```

Acceptance criteria:

```text
[ ] every online player appears globally
[ ] server grouping is correct
[ ] switching backend updates TAB
```

---
