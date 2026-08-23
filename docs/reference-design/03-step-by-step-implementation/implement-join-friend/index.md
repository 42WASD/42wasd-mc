# Implement `/join <friend>`

Algorithm:

```text
/join Alex
    ↓
resolve Alex Nakama user
    ↓
read presence
    ↓
is joinable?
    ↓
is runtime compatible with caller's current runtime?
```

If compatible:

```text
ensure target world ready
reserve one slot
transfer
```

If incompatible:

```text
create pending cross-runtime invite/join
show required runtime
offer launcher/server-project action
```

---
