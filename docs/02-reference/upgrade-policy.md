# Upgrade policy

How to safely upgrade proxies, runtimes, and images without downtime or breaking players.

## General rules

- **Test in a sandbox first** (a staging runtime), then roll to the cluster.
- **Pin versions** — don't float tags; record what's deployed.
- **One change at a time** to isolate regressions.
- Run the [acceptance test](acceptance-test.md) after each upgrade.

## Proxy (Velocity) upgrades

1. Deploy the new proxy image on a temp/parallel instance.
2. Verify forwarding secret still matches backends.
3. Do a rolling switch (drain/transfer players to lobby) before cutting over.
4. Back out if any backend fails to register.

## Runtime / Minecraft image upgrades

- For persistent maps: stop the world, snapshot PVC, upgrade, verify data intact.
- For vanilla: test a scratch player first.
- For Forge (fantasy): the Modrinth project (Step 14) must still resolve; verify Ambassador and ProxyCompatibleForge still pass.

## Java / machine upgrades

- Velocity 4.x needs Java 25; Forge 1.20.1 needs Java 21. Keep the base image's Java pinned to what the runtime declares in [RuntimeDefinition](runtime-definition.md).

## Rollback plan

- Keep previous image digests and configs recorded.
- On failure, revert the change and re-run acceptance (startup + data).

## See also

- [Step 13 — Fantasy Forge](../01-implement/step-13-fantasy-forge.md)
- [Step 14 — Modrinth](../01-implement/step-14-modrinth.md)
- [Operations: backups](../03-operations/backups.md)