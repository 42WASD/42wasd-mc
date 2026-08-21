# Phase 24 — Community map upload pipeline

Do not mount arbitrary user archives directly into a running server.

Pipeline:

```text
upload
  ↓
quarantine object storage
  ↓
size/type validation
  ↓
safe archive extraction
  ↓
malware scan
  ↓
world structure validation
  ↓
runtime compatibility validation
  ↓
review / automated policy
  ↓
publish immutable map revision
  ↓
create/update MapDefinition
```

A map revision should be immutable once published.

Example:

```text
backrooms-level-0@v1
backrooms-level-0@v2
```

---
