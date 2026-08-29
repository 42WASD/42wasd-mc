# Rollout order

Use this exact order:

```text
1. Velocity + one static Paper lobby
2. secure forwarding + backend isolation
3. TAB
4. ViaVersion/Backwards compatibility test
5. Nakama identity mapping
6. friends + parties
7. one static second backend + /join
8. World Controller
9. one persistent GameServerSet scale-to-zero map
10. portal -> wake -> transfer
11. exact map presence + TAB
12. random compatible map
13. fantasy Forge runtime + Ambassador + ProxyCompatibleForge
14. Modrinth Server Project
15. pending cross-runtime invite
16. mc-router edge wake
17. community upload pipeline
18. optional Agones ephemeral fleet
19. AI proximity bot
```

This order intentionally proves one contract at a time.

> **Note — curated proof sequence, not a 1:1 phase map.**
> The 19 items above are a *verification sequence* ("prove one contract at a
> time"), not a one-to-one enumeration of the index phases. The index order (in
> `03-step-by-step-implementation`) is the **build/reading order**; this list is
> the **verification order** and intentionally proves contracts before later
> dependencies exist. The two are related by phase number, not by position.
>
> Phases 0–2 (naming, repository structure, Kubernetes namespaces) are
> prerequisites completed before any of this order begins and so are not listed.
> Phases 3 (OpenKruiseGame install) and 4 (KEDA + observability install) appear
> where their capability is first exercised (item 9), and Phases 28 (backups)
> and 29 (monitoring) are cross-cutting operational concerns and are also not
> itemized here.

### Item → phase mapping

Each rollout item corresponds to a phase from the index (not sequential here by
design — the list proves one contract at a time, so a later index phase can be
verified before an earlier one):

| # | Rollout item | Index phase(s) |
|---|--------------|----------------|
| 1 | Velocity + one static Paper lobby | Phase 6 (Velocity), Phase 7 (Paper lobby) |
| 2 | secure forwarding + backend isolation | Phase 6 (forwarding secret) |
| 3 | TAB | Phase 8 |
| 4 | ViaVersion/Backwards | Phase 9 |
| 5 | Nakama identity mapping | Phase 5 (CockroachDB + Nakama) |
| 6 | friends + parties | Phase 15 |
| 7 | one static second backend + `/join` | Phase 16 (join-friend) |
| 8 | World Controller | Phase 13 |
| 9 | one persistent GameServerSet scale-to-zero map | Phase 3 (OKG), Phase 4 (KEDA), Phase 12 (map metadata) |
| 10 | portal → wake → transfer | Phase 21 |
| 11 | exact map presence + TAB | Phase 20 |
| 12 | random compatible map | Phase 21 (random routing) |
| 13 | fantasy Forge runtime + Ambassador + ProxyCompatibleForge | Phase 10 (Forge) |
| 14 | Modrinth Server Project | Phase 18 |
| 15 | pending cross-runtime invite | Phase 17 |
| 16 | mc-router edge wake | Phase 22 |
| 17 | community upload pipeline | Phase 26 (object storage), Phase 27 (upload pipeline) |
| 18 | optional Agones ephemeral fleet | Phase 24 |
| 19 | AI proximity bot | Phase 25 |

> **Prerequisite to items 8, 11 and 12:** Phase 11 (runtime catalog) and
> Phase 12 (map metadata) must be defined before the World Controller (item 8),
> exact presence (item 11) and random-map routing (item 12) can function. They
> are captured by their own phases and intentionally not restated as rollout
> items, but item 8 in particular assumes them.
>
> Item 5 ("Nakama identity mapping") bundles the Phase 5 CockroachDB + Nakama
> deployment; it appears here ahead of friends/parties (item 6), which depend
> on it.
>
> Item 9 now also lists Phase 4 (KEDA + observability), since a scale-to-zero
> map requires the KEDA `ScaledObject` from that phase.

---

## Incident recovery (operational)

Rollout phases 6–7 (Velocity + Paper lobby) have one recorded operational
incident: after a host reboot, prod-games pods CrashLooped due to **stale
CiliumEndpoint data carrying the old DHCP node IP**. The recovery runbook
(implementation page, Part III → `rollout-order`) documents the
diagnose → delete-stale-CEPs → restart-Cilium-agent sequence and the
prevention (pin the node IP before first bring-up).
