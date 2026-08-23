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
> Phases 0–3 (naming, repository structure, Kubernetes namespaces,
> OpenKruiseGame install) are prerequisites completed before any of this order
> begins and so are not listed. Phases 26 (backups) and 27 (monitoring) are
> cross-cutting operational concerns and are also not itemized here.

### Item → phase mapping

Each rollout item corresponds to a phase from the index (not sequential here by
design — the list proves one contract at a time, so a later index phase can be
verified before an earlier one):

| # | Rollout item | Index phase(s) |
|---|--------------|----------------|
| 1 | Velocity + one static Paper lobby | Phase 5 (Velocity), Phase 6 (Paper lobby) |
| 2 | secure forwarding + backend isolation | Phase 5 (forwarding secret) |
| 3 | TAB | Phase 7 |
| 4 | ViaVersion/Backwards | Phase 8 |
| 5 | Nakama identity mapping | Phase 4 (CockroachDB + Nakama) |
| 6 | friends + parties | Phase 14 |
| 7 | one static second backend + `/join` | Phase 15 (join-friend) |
| 8 | World Controller | Phase 12 |
| 9 | one persistent GameServerSet scale-to-zero map | Phase 3 (OKG), Phase 11 (map metadata) |
| 10 | portal → wake → transfer | Phase 20 |
| 11 | exact map presence + TAB | Phase 19 |
| 12 | random compatible map | Phase 12 (random routing) |
| 13 | fantasy Forge runtime + Ambassador | Phase 9 (Forge) |
| 14 | Modrinth Server Project | Phase 17 |
| 15 | pending cross-runtime invite | Phase 16 |
| 16 | mc-router edge wake | Phase 21 |
| 17 | community upload pipeline | Phase 25 |
| 18 | optional Agones ephemeral fleet | Phase 23 |
| 19 | AI proximity bot | Phase 24 |

> **Prerequisite to items 8, 11 and 12:** Phase 10 (runtime catalog) and
> Phase 11 (map metadata) must be defined before the World Controller (item 8),
> exact presence (item 11) and random-map routing (item 12) can function. They
> are captured by their own phases and intentionally not restated as rollout
> items, but item 8 in particular assumes them.
>
> Item 5 ("Nakama identity mapping") bundles the Phase 4 CockroachDB + Nakama
> deployment; it appears here ahead of friends/parties (item 6), which depend
> on it.

---
