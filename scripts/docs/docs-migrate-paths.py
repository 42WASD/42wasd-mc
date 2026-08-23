#!/usr/bin/env python3
"""One-time migration: rewrite all cross-references to the flattened SSOT paths.

After flattening reference-design and renaming sections to bare slugs, every
link that referenced the old 3-group + numbered layout must be rewritten. This
script:

  1. Builds an old-path-segment -> new-path-segment map from the manifest.
  2. Rewrites links in all docs/ markdown, mkdocs.yml, and scripts that point
     into the reference design.
  3. Rewrites progress.yaml keys and runbook `phase:` frontmatter.

Run:
    python3 scripts/docs/docs-migrate-paths.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
REF = REPO / "docs" / "reference-design"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from docs_manifest import load_sequence  # noqa: E402

# Explicit old->new section slug mapping (position + global numbers). Keyed by
# part slug. Built from the pre-migration tree.
OLD_NEW = {
    "01-understand-the-architecture-before-installing-anything": [
        ("00-0-the-one-sentence-idea", "the-one-sentence-idea"),
        ("01-1-why-the-tempting-one-tool-solves-everything-design-is-wrong",
         "why-the-tempting-one-tool-solves-everything-design-is-wrong"),
        ("02-2-the-complete-mental-model-seven-separate-layers",
         "the-complete-mental-model-seven-separate-layers"),
        ("03-3-runtime-classes-the-rule-that-makes-seamless-ux-possible",
         "runtime-classes-the-rule-that-makes-seamless-ux-possible"),
        ("04-4-proxy-decision-velocity-vs-gate-after-the-2026-08-audit",
         "proxy-decision-velocity-vs-gate-after-the-2026-08-audit"),
        ("05-5-the-selected-tool-stack", "the-selected-tool-stack"),
        ("06-6-why-several-attractive-projects-are-not-the-foundation",
         "why-several-attractive-projects-are-not-the-foundation"),
        ("07-7-social-state-why-nakama-belongs-beside-minecraft-rather-than-inside-it",
         "social-state-why-nakama-belongs-beside-minecraft-rather-than-inside-it"),
        ("08-8-dynamic-world-lifecycle", "dynamic-world-lifecycle"),
        ("09-9-end-to-end-user-experiences", "end-to-end-user-experiences"),
        ("10-10-plain-english-glossary", "plain-english-glossary"),
    ],
    "02-how-to-interpret-the-actual-tools": [
        ("00-11-capability-cheat-sheet", "capability-cheat-sheet"),
        ("01-12-maturity-and-deployment-tiers", "maturity-and-deployment-tiers"),
        ("02-13-current-verification-notes-2026-08-19",
         "current-verification-notes-2026-08-19"),
        ("03-14-failure-modes-you-must-design-for", "failure-modes-you-must-design-for"),
        ("04-15-observability", "observability"),
        ("05-16-security-boundaries", "security-boundaries"),
    ],
    "03-step-by-step-implementation": [
        ("00-17-phase-0-decide-names-before-deploying", "decide-names-before-deploying"),
        ("01-18-phase-1-create-repository-structure", "create-repository-structure"),
        ("02-19-phase-2-create-kubernetes-namespaces", "create-kubernetes-namespaces"),
        ("03-20-phase-3-deploy-cockroachdb-and-nakama", "deploy-cockroachdb-and-nakama"),
        ("04-21-phase-4-deploy-velocity", "deploy-velocity"),
        ("05-22-phase-5-deploy-the-paper-lobby", "deploy-the-paper-lobby"),
        ("06-23-phase-6-install-tab", "install-tab"),
        ("07-24-phase-7-add-viaversion-and-viabackwards", "add-viaversion-and-viabackwards"),
        ("08-25-phase-8-deploy-the-forge-1-20-1-fantasy-runtime",
         "deploy-the-forge-1-20-1-fantasy-runtime"),
        ("09-26-phase-9-define-the-runtime-catalog", "define-the-runtime-catalog"),
        ("10-27-phase-10-define-map-metadata", "define-map-metadata"),
        ("11-28-phase-11-build-the-world-controller", "build-the-world-controller"),
        ("12-29-phase-12-build-networkbridge-for-velocity", "build-networkbridge-for-velocity"),
        ("13-30-phase-13-implement-friends-and-parties", "implement-friends-and-parties"),
        ("14-31-phase-14-implement-join-friend", "implement-join-friend"),
        ("15-32-phase-15-implement-pending-cross-runtime-invites",
         "implement-pending-cross-runtime-invites"),
        ("16-33-phase-16-publish-modrinth-server-projects", "publish-modrinth-server-projects"),
        ("17-34-phase-17-add-packwiz-ci", "add-packwiz-ci"),
        ("18-35-phase-18-add-exact-world-dimension-tab-information",
         "add-exact-world-dimension-tab-information"),
        ("19-36-phase-19-implement-the-glitch-random-portal", "implement-the-glitch-random-portal"),
        ("20-37-phase-20-add-mc-router", "add-mc-router"),
        ("21-38-phase-21-add-idle-sleep", "add-idle-sleep"),
        ("22-39-phase-22-add-agones-only-for-session-worlds", "add-agones-only-for-session-worlds"),
        ("23-40-phase-23-add-ai-proximity-chat", "add-ai-proximity-chat"),
        ("24-41-phase-24-community-map-upload-pipeline", "community-map-upload-pipeline"),
        ("25-42-phase-25-backups", "backups"),
        ("26-43-phase-26-monitoring", "monitoring"),
        ("27-44-phase-27-rollout-order", "rollout-order"),
    ],
    "04-technical-reference": [
        ("00-45-recommended-source-of-truth-model", "recommended-source-of-truth-model"),
        ("01-46-runtimedefinition-schema", "runtimedefinition-schema"),
        ("02-47-mapinstance-schema", "mapinstance-schema"),
        ("03-48-routing-state-machine", "routing-state-machine"),
        ("04-49-random-routing-scoring", "random-routing-scoring"),
        ("05-50-invite-policy", "invite-policy"),
        ("06-51-world-readiness-contract", "world-readiness-contract"),
        ("07-52-network-security-checklist", "network-security-checklist"),
        ("08-53-functional-acceptance-test", "functional-acceptance-test"),
        ("09-54-performance-principles", "performance-principles"),
        ("10-55-upgrade-policy", "upgrade-policy"),
        ("11-56-why-this-architecture-is-intentionally-not-fully-automatic-on-day-one",
         "why-this-architecture-is-intentionally-not-fully-automatic-on-day-one"),
    ],
    "05-current-verification-references": [
        ("00-57-final-architecture-recommendation", "final-architecture-recommendation"),
    ],
}

# old group path -> new flat path (for part index pages)
OLD_GROUP = {
    "background/01-understand-the-architecture-before-installing-anything":
        "01-understand-the-architecture-before-installing-anything",
    "background/02-how-to-interpret-the-actual-tools":
        "02-how-to-interpret-the-actual-tools",
    "build/03-step-by-step-implementation":
        "03-step-by-step-implementation",
    "reference/04-technical-reference":
        "04-technical-reference",
    "reference/05-current-verification-references":
        "05-current-verification-references",
}

# Build a flat list of (old_segment, new_segment), longest first, so that
# `reference-design/background/01-.../00-0-...` is replaced before `reference-design/...`.
def all_replacements() -> list[tuple[str, str]]:
    repls = []
    # Full path replacements: reference-design/<group>/<part>/<old_section>/ -> new
    for part, secs in OLD_NEW.items():
        group = next((g for g, p in OLD_GROUP.items() if p == part), None)
        if not group:
            continue
        for old_sec, new_sec in secs:
            repls.append((f"{group}/{old_sec}", f"{part}/{new_sec}"))
    # Part-only path: reference-design/<group> -> reference-design/<part>
    for group, part in OLD_GROUP.items():
        repls.append((f"reference-design/{group}", f"reference-design/{part}"))
        # Also bare relative form used in platform map / Contents (no prefix)
        repls.append((f"{group}/", f"{part}/"))
    # Bare relative part/section references (no reference-design/ prefix), e.g.
    # Contents lists: `<old_sec>/index.md` -> `<new_sec>/index.md`
    for part, secs in OLD_NEW.items():
        for old_sec, new_sec in secs:
            repls.append((f"{old_sec}/", f"{new_sec}/"))
    # Sort longest-first so more specific paths replace first.
    repls.sort(key=lambda r: len(r[0]), reverse=True)
    return repls


REPLACEMENTS = all_replacements()


def rewrite_paths(text: str) -> str:
    for old, new in REPLACEMENTS:
        text = text.replace(old, new)
    return text


def rewrite_file(path: Path) -> bool:
    if not path.exists():
        return False
    original = path.read_text()
    new = rewrite_paths(original)
    if new != original:
        path.write_text(new)
        return True
    return False


def main() -> int:
    changed = 0
    targets = [
        REPO / "docs", REPO / "mkdocs.yml",
        REPO / "README.md", REPO / "scripts",
    ]
    for base in targets:
        if not base.exists():
            continue
        if base.is_file():
            changed += int(rewrite_file(base))
            continue
        for f in sorted(base.rglob("*.md")) + sorted(base.rglob("*.yml")) \
                + sorted(base.rglob("*.py")):
            changed += int(rewrite_file(f))
    print(f"Rewrote paths in {changed} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())