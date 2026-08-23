#!/usr/bin/env python3
"""One-time migration: flatten reference-design and rename sections to bare slugs.

Moves the 3-group layout (background/build/reference) into a flat parts list at
docs/reference-design/<NN-part-slug>/<bare-section-slug>/index.md, matching the
ubuntu-server-iac SSOT layout. Part folders keep their leading position number
(e.g. `01-understand-...`); section folders drop the numeric + phase prefix.

Old section slug shapes:
    NN-NN-<slug>            (concept/reference sections, e.g. 00-11-capability-...)
    NN-PP-phase-N-<slug>    (build phases, e.g. 00-17-phase-0-decide-names-...)

New section slug:
    <slug>  (e.g. capability-cheat-sheet, decide-names-before-deploying)

Run from repo root:
    python3 scripts/docs/docs-flatten-sequence.py
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
REF = REPO / "docs" / "reference-design"

GROUPS = ["background", "build", "reference"]

PREFIX = re.compile(r"^\d+-\d+(?:-phase-\d+)?-")


def strip_prefix(name: str) -> str:
    return PREFIX.sub("", name)


def git_mv(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "mv", str(src), str(dst)], check=True,
                   cwd=REPO)


def main() -> int:
    # Mapping: old part dir (absolute) -> (part_slug, list[(old_section, new_slug)])
    plans: list[tuple[Path, str, list[tuple[Path, str]]]] = []
    for group in GROUPS:
        gdir = REF / group
        if not gdir.is_dir():
            continue
        for part_dir in sorted(gdir.iterdir()):
            if not part_dir.is_dir():
                continue
            part_slug = part_dir.name
            sections = []
            for sec_dir in sorted(part_dir.iterdir()):
                if not sec_dir.is_dir():
                    continue
                if (sec_dir / "index.md").exists():
                    sections.append((sec_dir, PREFIX.sub("", sec_dir.name)))
                else:
                    # nested subfolder not holding index directly — keep as-is
                    sections.append((sec_dir, sec_dir.name))
            plans.append((part_dir, REF / part_slug, sections))

    # Stage 1: rename the section folders (bare slug) in place, under old part dir.
    for part_dir, _, sections in plans:
        for old_dir, new_slug in sections:
            if old_dir.name == new_slug:
                continue
            target = part_dir / new_slug
            print(f"  mv {old_dir.name} -> {new_slug}")
            git_mv(old_dir, target)

    # Stage 2: move part dir up one level to REF (flatten).
    for part_dir, new_dir, _ in plans:
        if part_dir == new_dir:
            continue
        print(f"  flatten {part_dir.name} -> {new_dir.name}")
        git_mv(part_dir, new_dir)

    # Stage 3: remove the now-empty group dirs.
    for group in GROUPS:
        gdir = REF / group
        if gdir.is_dir():
            shutil.rmtree(gdir, ignore_errors=True)
            print(f"  removed group dir {group}")

    print("Flatten + rename complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())