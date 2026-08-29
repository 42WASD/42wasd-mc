# Agent Instructions

## RESEARCH ONLINE WHEN STUCK — MANDATORY

- If you cannot find the correct solution, design, or configuration from the
  repository/context alone (or after 2-3 failed attempts), **STOP guessing and search
  the authoritative source online immediately** (official docs, GitHub issues,
  the software's own documentation) before continuing.
- This is a hard rule, not a last resort. Do not thrash or repeatedly try
  variations of the same guess. When unsure of the *right design*, look up the
  vendor's documented best practice first, then apply it.
- Record what you learned from the research in the runbook / session memory.

### Config/format errors: search the authoritative source BEFORE hand-editing

- If a generated or template-driven config (e.g. a TOML/YAML consumed by a
  container image) is rejected as **invalid**, or a workload crashes with a
  config/parse error, **do not blindly keep tweaking the fragment you think is
  wrong.** First find the **authoritative default/schema** the tool actually
  loads:
  1. Inspect the running container's real config file (the exact file the
     process reads, not just the one you mounted) — `kubectl exec ... cat <path>`
     / the image's `templates/` dir in its GitHub source.
  2. If it came from a default-configs repo (e.g. itzg images pull from
     `Shonz1/minecraft-default-configs`), fetch that **default template** and
     diff your snippet against it. The image may append/merge sections you
     didn't provide (e.g. `[forced-hosts]`) that reference servers you never
     defined — a partial override is often the bug.
  3. Many configs must be **complete**, not partial. Provide the whole file
     (including empty-but-valid sections) rather than a fragment.
  4. Confirm **which copy the process actually loads** and whether the mounted
     file reliably overwrites the image's downloaded default (e.g.
     `SYNC_SKIP_NEWER_IN_DESTINATION`/`--skip-existing` can silently keep the
     old default).
- This applies to Velocity/BungeeCord/Paper/forks and any template-driven
  config, not just Minecraft.

## Repository Layout & File Placement (Overarching Rule)

- **Whenever creating or adding any new file, always stop and consider whether
  it belongs in a new subfolder or in an existing, more appropriate location.
  Do not default to the top of a folder.**
- If a new file is one of several related files (e.g. scripts for a domain),
  group them under a dedicated subfolder rather than scattering them.
- When in doubt, check the surrounding repo structure first (e.g. `scripts/`
  already has a domain subfolder `docs/`; `infra/` has `ansible/`,
  `kubernetes/`, `docs/`, `inventory/`, `autoinstall/`, `developer/`, `tofu/`)
  and place the file to match the established convention.

## Python Environment

- **Always use `uv` to manage Python virtual environments and dependencies.**
  - Python projects in this repo live under `projects/` and are managed via `pyproject.toml` + `uv.lock`.
  - Create/activate the venv and install all deps: `uv sync` (run from the `projects/` directory).
  - Run a tool from the venv without activating it: `uv run <command>` (e.g. `uv run mkdocs build`).
  - Activate manually if needed: `source projects/.venv/bin/activate`.
  - Do **not** use `python3 -m venv`, `pip`, or plain `requirements.txt` directly.
- When a task involves Python, prefer `uv` for dependency management and venv creation.
- **MkDocs docs site:** config is at repo root (`mkdocs.yml`), sources in `docs/`. Build/serve from `projects/` using `uv run mkdocs build --strict -f ../mkdocs.yml` (or `uv run mkdocs serve -f ../mkdocs.yml`). The generated `site/` lands at the repo root.

## Verification — MANDATORY before commit

- **Before committing ANY change** to docs, the SSOT manifest
  (`docs/reference-design/_sequence.yaml`), a generator, or `mkdocs.yml`, you
  MUST run the full verification pipeline and it MUST pass:

  ```bash
  bash scripts/docs/verify.sh          # full: validate -> tests -> strict build
  bash scripts/docs/verify.sh --stage  # skip the slow mkdocs build (fast)
  ```

  This is exactly what CI runs, so **local = CI**. A change is not "done" until
  `verify.sh` reports **`VERIFY OK`**. Never commit, open a PR, or push if the
  pipeline fails or was skipped.
- The **golden test** asserts generators are idempotent: it fails if committed
  generated output (`mkdocs.yml` nav, `docs/implementation/index.md`) doesn't
  match what the generators produce. When you edit the manifest or a generator,
  regenerate and **commit the regenerated output together** with the change.

## Runbook — record every command you run

- **Whenever you run commands to implement, configure, verify, or change the
  infrastructure, you MUST record them in the runbook immediately** — same
  turn as the work, not later. This is a hard rule, not a nice-to-have.
- **Where:** `docs/implementation/_runbook/<part>/phase-<NN>-<slug>.md`
  (one file per phase; pick the closest existing phase file or create one).
- **What to include:** the exact commands run (verbatim), what they did, and
  what was verified/observed. Use a code block, in the appropriate section.
- **Do not** record transient/exploratory probing or failed attempts unless
  they changed the system or are instructive.
- **After recording, regenerate and rebuild:**
  `python3 scripts/docs/docs-generate-implementation.py` then
  `cd projects && uv run mkdocs build --strict -f ../mkdocs.yml`
- If you complete a phase, also bump its status in `docs/implementation/progress.yaml`.
## Password-based SSH / remote commands (sshpass)

- When a remote host must be reached with a **password** (no key installed),
  never ask for it in chat for the first connection — prompt the user to run
  it interactively, or use key-based auth / `BatchMode` and let it fail
  cleanly.
- **Once the user has typed the password into the chat** (a later turn), you
  may use `sshpass` for subsequent commands non-interactively. Read it into
  an env var rather than inlining it:
  ```bash
  SSHPASS='<password-from-user>' sshpass -e ssh -o StrictHostKeyChecking=accept-new user@host 'command'
  ```
- `sshpass -e` (env var) over `sshpass -p '<pw>'` — keeps the password out of
  `ps` output and shell history.
- For recurring access, prefer installing a key (`ssh-copy-id`) so later
  turns need no password at all. Never echo the password back, never commit
  it, never store it in a file inside the repo.

## Doc-impact — check docs for staleness after live commands

- **After any successful run of new/implementing commands** (anything that
  installed, configured, created, renamed, scaled, or removed something on
  the host or cluster), run a quick doc-impact check **before finishing the
  turn**:

  **Step 1 — smart diff:** describe what changed and retrieve the docs that
  talk about the same things (hybrid FTS5-BM25 + fuzzy over a committed
  SQLite index):
  ```bash
  cd projects
  uv run python ../scripts/docs/doc-impact/impact_search.py "what changed"
  ```
  **Step 2 — load and reconcile:** fix stale docs in the same turn.
  **Step 3 — regression battery:**
  ```bash
  uv run pytest tests/test_doc_impact.py -q -m quick   # fast host-only
  uv run pytest tests/test_doc_impact.py -q            # full probe
  ```
- Expectations live in `scripts/docs/doc-impact/live-expectations.yaml`
  (ships with skipped placeholders — delete `skip:` and point at real
  infrastructure). The committed index (`doc-index.db`) self-updates via the
  post-commit hook; enable once per clone:
  `bash scripts/docs/doc-impact/setup-git-hooks.sh`
