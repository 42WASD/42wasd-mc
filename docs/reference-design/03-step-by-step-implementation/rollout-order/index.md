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
9. one persistent StatefulSet scale-to-zero map
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
> The 19 items above are a *verification sequence* ("prove one contract at a time"), not a
> one-to-one enumeration of Phases 0–27. Phases 0–2 (naming, repository structure, Kubernetes
> namespaces) are prerequisites completed before any of this order begins and so are not listed.
> Phases 25 (backups) and 26 (monitoring) are cross-cutting operational concerns and are also not
> itemized here.
>
> **Prerequisite to items 8, 11 and 12:** Phase 9 (runtime catalog) and Phase 10 (map metadata)
> must be defined before the World Controller (item 8), exact presence (item 11) and random-map
> routing (item 12) can function. They are captured by their own phases and are intentionally not
> restated as rollout items, but item 8 in particular assumes them.
>
> Item 5 ("Nakama identity mapping") bundles the Phase 3 CockroachDB + Nakama deployment; it
> appears here ahead of friends/parties (item 6), which depend on it.

---
