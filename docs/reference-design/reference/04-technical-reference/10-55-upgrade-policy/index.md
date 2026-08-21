# Upgrade policy

Pin tested versions.

Example release record:

```yaml
platformRelease: 2026-08-r1

components:
  velocity: "4.0.0"
  java: "25"
  tab: "6.1.2"
  viaversion: "5.11.0"
  viabackwards: "5.11.0"
  nakama: "3.40.0"
  minecraftServerImage: "2026.8.0"
```

For components without a desired fixed semantic release in this document:

```text
pin tested container digest
record Git commit/release
upgrade in staging
```

Never let `latest` redefine production overnight.

---
