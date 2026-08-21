# Why this architecture is intentionally not “fully automatic” on day one

The difficult part is not launching another Minecraft process.

The difficult part is maintaining these invariants:

```text
correct client runtime
correct authenticated UUID
correct world revision
correct capacity
correct party routing
correct persistent data
correct readiness
correct forwarding/security
```

A small explicit World Controller is easier to reason about than chaining five “automatic server cloud” plugins whose responsibilities overlap.

Automation should come after the contracts are clear.

---
