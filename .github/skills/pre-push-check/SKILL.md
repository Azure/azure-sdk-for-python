---
name: pre-push-check
description: Pre-push hook for azure-sdk-for-python. Before code is pushed, it analyzes the files changed against the target branch and runs the required CI checks locally so failures are caught before CI. Catches the easy-to-forget repo-wide checks (CSpell spelling and broken-link verification) for non-SDK changes, and runs the per-package SDK checks (pylint, mypy, pyright, cspell, changelog, etc.) via the azure-sdk-mcp tooling. Use before pushing/opening a PR.
---

# Pre-Push Check Skill

## Purpose

CI runs **repo-wide checks** (which apply even to non-SDK changes like docs, `.github/`, READMEs) and
**per-package checks**. This skill emulates a pre-push hook: it detects what changed vs the target
branch, runs only the relevant checks, and reports/fixes failures **before** the push so CI passes
first try.

> **No hardcoded commands.** Describe *what* to run and *which* scripts/tools to use — flags and paths
> drift. Read each script's `param(...)` block / the `azpysdk` / MCP tool help to build the exact
> command at runtime.

## Prerequisites

- `pwsh` (PowerShell 7+), `git`, Node.js (`npx`) on PATH for the spelling/link scripts.
- For SDK package checks via MCP, run `azsdk_verify_setup` first if the environment may not be set up.

## Steps

**0. Confirm first.** Ask the user whether they want to run local validation to make sure CI will pass
(it can take minutes and hit the network), summarizing what will run based on detected changes. Stop if
they decline.

**1. Target branch.** Identify the branch the PR targets (default the repo's main branch; confirm if
ambiguous). Repo-wide checks diff against it with a three-dot (`target...source`) comparison.

**2. Changed files.** Diff current branch vs target (three-dot, excluding deletes) and classify:
- **SDK package changes** — under `sdk/<service>/<package>/...`; group by package dir (the one with
  `pyproject.toml` / `setup.py`).
- **Repo-wide / non-SDK** — everything else (`doc/`, `eng/`, `.github/`, root `*.md`, scripts).

If nothing changed, report and stop.

**3. Repo-wide checks (always, when anything changed).** Run from the repo root; mirror CI's
fail-on-error behavior. These are the checks most often missed on non-SDK work:
- **CSpell** — `eng/common/scripts/check-spelling-in-changed-files.ps1`, pointed at the current and
  target branch. Honors `.vscode/cspell.json` plus any service-level `cspell.json`/`cspell.yaml`.
- **Verify-Links** — `eng/common/scripts/Verify-Links.ps1` on the changed markdown only (full recursion
  is slow). Enable link-guidance to catch the common failures: disallowed relative links and links
  hard-coding `main` (https://aka.ms/azsdk/guideline/links). Ignore transient 403/timeouts; focus on
  `404`/host-not-found and guidance violations.

**4. Per-package SDK checks (per changed package).** Prefer **azure-sdk-mcp**:
- `azsdk_package_run_check` with `packagePath` = the package dir (covers spelling, changelog, README,
  snippets, linting, formatting, or all at once; can auto-fix).
- `azsdk_package_run_tests` when source code changed.

Fallback: `azpysdk` from the package dir (see `doc/eng_sys_checks.md`). Check `pyproject.toml` for
opted in/out checks; scope to changed packages only.

**5. Report and gate.** Summarize PASS/FAIL per check with offending files/lines.
- All pass → safe to push.
- Any fail → do **not** advise pushing; remediate, then re-run only the failed checks until green:
  - Spelling: fix the typo, or add intentional words to the service-level `cspell.json`/`cspell.yaml`,
    `.vscode/cspell.json` (repo-wide), or an inline `# cspell:ignore <word>`.
  - Links: fix the target; replace `.../blob/main/...` links per the guidance; add valid-but-unreachable
    links to `eng/ignore-links.txt`.
  - SDK failures: use `fix-pylint` / `fix-mypy` / `fix-sphinx` / `fix-black` or the
    `azsdk_package_run_check` fix option.
