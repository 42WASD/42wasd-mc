---
phase: 03-step-by-step-implementation/install-openkruisegame
---
# Install OpenKruiseGame (new Phase 3)

## What was done

Created the `install-openkruisegame` phase (new Phase 3, inserted after
`create-kubernetes-namespaces`) so the World Controller's `GameServerSet`
driving is grounded in an actual platform install step. Verified the install
mechanics against the current OpenKruiseGame docs:

- OKG requires **both** Kruise and Kruise-Game, Kubernetes >= 1.18.
- `helm repo add openkruise` → `helm install kruise openkruise/kruise` →
  `helm install kruise-game openkruise/kruise-game`.
- Installs the `game.kruise.io/v1alpha1` API group (GameServerSet, GameServer).
- Also added to this phase: an OKG→World Controller ownership note (World
  Controller scales the GameServerSet via narrow RBAC; it does not install OKG).

## Effects on numbering

Inserting this phase after `create-kubernetes-namespaces` shifted all later
phases +1. Regenerated nav + implementation page; updated the hand-written
prose "Phase N" references:

- `social-state...`: "Phase 5" (Paper lobby) → "Phase 6"
- `current-verification-notes-2026-08-19`: "Phase 5" → "Phase 6"
- `rollout-order`: "Phases 0–27" → "0–28"; CockroachDB "Phase 3" → "4";
  runtime catalog "9 → 10"; map metadata "10 → 11"; added item→phase mapping
  table.
- `docs/implementation/progress.yaml`: inserted Phase 3 comment + renumbered.

## Commands

```bash
# Add the new phase folder + page, then register it in the manifest
# (edits to _sequence.yaml, install-openkruisegame/index.md)

# Regenerate nav + implementation page (must match committed output)
cd /home/jyao/42wasd-mc
python3 scripts/docs/docs-generate-nav.py
python3 scripts/docs/docs-generate-implementation.py

# Full verification pipeline
bash scripts/docs/verify.sh
```

## Result

`bash scripts/docs/verify.sh` → **VERIFY OK** (Layer 1+2 VALIDATION OK, 7
pytest passed, strict mkdocs build succeeded). Generated files were staged so
the golden test compared against the regenerated output.

## Related doc edits (same review pass)

- `social-state...` §7.1.0: corrected the offline/cracked auth model to an
  **in-game auth gate** — player joins, lands on a login stage, completes
  Discord/Google OAuth there, is linked to a Nakama account, then routed on.
- `deploy-cockroachdb-and-nakama`: aligned the flow diagram to the gate model.
- `add-exact-world-dimension-tab-information`: added the missing **backend-side
  presence bridge** description (a per-runtime plugin/mod that reports
  dimension changes keyed by UUID to NetworkBridge/Nakama) — closing the gap
  where exact dimension data never reached TAB.
- `plain-english-glossary`: added "Auth gate".