#!/usr/bin/env python3
"""Split the Minecraft network architecture source doc into a reference-design tree.

Output layout under docs/reference-design/:

    docs/reference-design/
        index.md                    <- overview page
        background/                 <- Parts I, II (concepts & design)
        build/                      <- Part III (implementation phases)
        reference/                  <- Parts IV, V (technical reference & references)

Each group contains one folder per "Part", and one folder per numbered section:

    <group>/<NN>-<part-slug>/index.md
    <group>/<NN>-<part-slug>/<NN>-<section-slug>/index.md

The source doc is internally inconsistent: Part titles are H1; sections are
sometimes H1 and sometimes H2, and some H2s are decimal subsections (e.g.
`## 20.1 Why CockroachDB`). We treat a heading as a *section boundary* when it
is H1/H2 and starts with a plain-integer number (e.g. `17. Phase 0 ...`) — but
NOT a decimal number (`2.1 ...`), which stays inside its parent section.

Run:
    python3 scripts/docs/docs-split-minecraft.py
"""

from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
SRC = REPO / "sources" / "verified_dynamic_minecraft_network_architecture_2026-08-19.md"
OUT = REPO / "docs" / "reference-design"

TITLE = "Verified Dynamic Minecraft Network / Runtime Architecture"

PART_RE = re.compile(r"^Part\s+(\S+)\s*[—-]?\s*(.*)$")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
# A section boundary's *text* (no leading #): a plain integer followed by a dot
# then NOT another digit (so decimal subsections like 2.1 are excluded).
SECTION_TEXT_RE = re.compile(r"^(\d+)\.(?!\d)\s*(.*)$")

# Map Roman part numeral -> reference-design group.
GROUP_OF_PART = {"I": "background", "II": "background",
                 "III": "build",
                 "IV": "reference", "V": "reference"}


def slugify(name: str) -> str:
    name = name.strip().lower()
    name = name.replace("—", "-").replace("–", "-").replace("/", "-")
    name = re.sub(r"[^a-z0-9]+", "-", name)
    name = re.sub(r"-+", "-", name).strip("-")
    return name or "untitled"


def roman_to_int(roman: str) -> int:
    vals = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100}
    total = 0
    prev = 0
    for ch in reversed(roman.upper()):
        cur = vals.get(ch, 0)
        total += -cur if cur < prev else cur
        prev = cur
    return total


def is_part(text: str) -> bool:
    return bool(PART_RE.match(text))


FENCE_RE = re.compile(r"^\s*(```+|~~~+)")


def split_blocks(lines):
    """Return [start, end, level, text] for real headings, ignoring fenced code."""
    blocks = []
    in_fence = False
    for i, ln in enumerate(lines):
        if FENCE_RE.match(ln):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = HEADING_RE.match(ln)
        if m:
            blocks.append([i, len(lines), len(m.group(1)), m.group(2).strip()])
    for j in range(len(blocks) - 1):
        blocks[j][1] = blocks[j + 1][0]
    return blocks


def main() -> int:
    if not SRC.exists():
        print(f"Missing source: {SRC}", file=sys.stderr)
        return 1

    lines = SRC.read_text().split("\n")
    blocks = split_blocks(lines)
    part_idxs = [i for i, b in enumerate(blocks) if is_part(b[3])]

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    # Overview page: everything before the first part.
    first_part_line = blocks[part_idxs[0]][0]
    overview = "\n".join(lines[:first_part_line]).strip()
    overview = re.sub(r"^# .*$", f"# {TITLE}", overview, count=1, flags=re.M)
    (OUT / "index.md").write_text(overview + "\n")

    part_summary: list[tuple[str, str, str]] = []  # (roman, title, slug)
    group_nav: dict[str, list] = {g: [] for g in ("background", "build", "reference")}

    for p_idx, b in enumerate(part_idxs):
        part_line = blocks[b][0]
        part_end = blocks[part_idxs[p_idx + 1]][0] if p_idx + 1 < len(part_idxs) else len(lines)
        m = PART_RE.match(blocks[b][3])
        roman = m.group(1)
        part_title = (m.group(2) or "").strip()
        part_num = roman_to_int(roman)
        group = GROUP_OF_PART.get(roman.upper(), "reference")

        part_slug = f"{part_num:02d}-{slugify(part_title)}"
        gdir = OUT / group
        gdir.mkdir(exist_ok=True)
        part_dir = gdir / part_slug
        part_dir.mkdir()

        # Section boundaries inside this part: H1/H2 (level<=2) whose text
        # starts with a plain-integer number (excludes decimal subsections).
        secs = [
            s for s in range(len(blocks))
            if blocks[s][0] > part_line and blocks[s][0] < part_end
            and blocks[s][2] <= 2
            and SECTION_TEXT_RE.match(blocks[s][3])
        ]

        first_sec = secs[0] if secs else None
        landing_end = blocks[first_sec][0] if first_sec is not None else part_end
        part_intro = "\n".join(lines[part_line:landing_end]).strip()
        if not part_intro:
            part_intro = f"# Part {roman}"
        (part_dir / "index.md").write_text(part_intro + "\n")

        part_nav = [{"Overview": f"reference-design/{group}/{part_slug}/index.md"}]

        for s_idx, s in enumerate(secs):
            s_line = blocks[s][0]
            s_end = blocks[secs[s_idx + 1]][0] if s_idx + 1 < len(secs) else part_end
            s_text = blocks[s][3]

            body_lines = lines[s_line + 1 : s_end]
            body = "\n".join(body_lines).strip()
            body = re.sub(
                r"(?m)^(#{3,6})\s+",
                lambda mm: "#" * (int(len(mm.group(1))) - 1) + " ",
                body,
            )

            sm = SECTION_TEXT_RE.match(s_text)
            display_title = sm.group(2).strip() if sm and sm.group(2) else s_text

            sec_slug = f"{s_idx:02d}-{slugify(s_text)}"
            sec_dir = part_dir / sec_slug
            sec_dir.mkdir()
            (sec_dir / "index.md").write_text(f"# {display_title}\n\n{body}\n")

            part_nav.append({display_title: f"reference-design/{group}/{part_slug}/{sec_slug}/index.md"})

        # Append a table of contents to the part landing page.
        if secs:
            toc = ["", "---", "", "## Contents", ""]
            for s_idx, s in enumerate(secs):
                sm = SECTION_TEXT_RE.match(blocks[s][3])
                disp = sm.group(2).strip() if sm and sm.group(2) else blocks[s][3]
                sec_slug = f"{s_idx:02d}-{slugify(blocks[s][3])}"
                toc.append(f"- [{disp}]({sec_slug}/index.md)")
            with (part_dir / "index.md").open("a") as fh:
                fh.write("\n".join(toc) + "\n")

        group_nav[group].append({f"{roman} — {part_title}": part_nav})
        part_summary.append((roman, part_title, f"{group}/{part_slug}"))

    # Append a platform map to the overview page.
    with (OUT / "index.md").open("a") as fh:
        fh.write("\n---\n\n## Platform Map\n\n")
        for roman, part_title, rel in part_summary:
            fh.write(f"- [{roman} — {part_title}]({rel}/index.md)\n")

    print(f"Split {len(lines)} lines into {len(part_summary)} parts under {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())