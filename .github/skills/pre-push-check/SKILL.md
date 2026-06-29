---
name: pre-push-check
description: Pre-push hook for azure-sdk-for-python. Before code is pushed, it analyzes the files changed against the target branch and runs the required CI checks locally so failures are caught before CI. Catches the easy-to-forget repo-wide checks (CSpell spelling and broken-link verification) for non-SDK changes, and runs the per-package SDK checks (pylint, mypy, pyright, cspell, changelog, etc.) via the azure-sdk-mcp tooling. Use before pushing/opening a PR.
---

# Pre-Push Check Skill

## Purpose

CI for this repo runs a mix of **repo-wide checks** and **per-package checks**. Repo-wide checks apply even when working on non-SDK code (docs, `.github/`, root markdown, samples, READMEs).

This skill emulates a pre-push hook: it figures out exactly what changed relative to the
target branch, runs only the checks relevant to those changes, and reports failures (with fixes where
possible) **before** the push so CI passes on the first try.

It prefers the `azure-sdk-mcp` `azsdk_package_run_check` / `azsdk_package_run_tests` tools for
per-package checks, and uses the repo's PowerShell scripts for the repo-wide checks that the MCP
tooling does not cover.

> **No hardcoded commands.** This skill intentionally describes *what* to run and *which* scripts/tools
> to use, not exact command invocations — flags and paths drift over time. Determine the precise
> command by reading the script's parameter block (`Get-Help` / the `param(...)` header) and the
> `azpysdk` / MCP tool help at execution time.

## When to use

- The user is about to `git push` or open a PR and wants to avoid CI failures.
- The user explicitly asks to run checks locally or validate changes.
- After making non-SDK edits (docs, eng, `.github`, READMEs) where spelling/link checks commonly fail.

## Prerequisites

- `pwsh` (PowerShell 7+), `git`, and Node.js (`npx`) on PATH — required for the spelling and link scripts.
- For SDK package checks via MCP, the environment must be set up. If unsure, run `azsdk_verify_setup` first.

## Steps

### 0. Confirm with the user before running validation

Before running anything, **ask the user whether they want to run local validation to make sure CI will
pass** (the checks can take several minutes and may hit the network). Briefly summarize what will run
based on the detected changes (repo-wide spelling/link checks, plus which SDK packages, if any).

- If the user declines, stop — do not run the checks.
- If the user confirms, proceed with the steps below.

### 1. Determine the target (base) branch

Identify the branch the PR will target so the diff matches CI. Default to the repo's main branch, and
confirm with the user if the upstream/target is ambiguous. The repo-wide checks diff against this
target using a three-dot (`target...source`) comparison.

### 2. Compute the changed files

Diff the current branch against the target (three-dot, excluding deleted files) and classify the
results into:

- **SDK package changes** — paths under `sdk/<service>/<package>/...`. Group by package directory
  (the directory containing `pyproject.toml` / `setup.py`).
- **Repo-wide / non-SDK changes** — everything else (`doc/`, `eng/`, `.github/`, root `*.md`,
  scripts, etc.). These still flow through the repo-wide spelling and link checks.

If there are no changes vs the target, report that and stop.

### 3. Run the repo-wide checks (always, when there are changes)

These run on every PR regardless of which files changed and are the ones most often missed on non-SDK
work. Run them from the repo root and mirror CI's failure behavior (exit non-zero on errors).

**3a. CSpell — spelling on changed files**

Use `eng/common/scripts/check-spelling-in-changed-files.ps1`, pointing it at the current branch and the
target branch. It honors `.vscode/cspell.json` plus any service-level `cspell.json`/`cspell.yaml`. Read
the script's parameter block to set the source/target committishes and to make it fail on errors.

**3b. Verify-Links — broken / non-compliant links on changed markdown**

Use `eng/common/scripts/Verify-Links.ps1` against only the changed markdown files (full-repo recursion
is slow and unnecessary pre-push). Enable the link-guidance check so it catches the common CI failures:
disallowed relative links and links that hard-code the `main` branch (see
https://aka.ms/azsdk/guideline/links). Read the script's parameter block for the current argument names.

- Network link checks can be slow or flaky; transient 403/timeout on external hosts are usually not the
  failure to fix — focus on `404`/host-not-found and guidance violations.

### 4. Run the per-package SDK checks (for each changed SDK package)

For every distinct changed SDK package directory, prefer the **azure-sdk-mcp** tooling:

- `azsdk_package_run_check` with `packagePath` = the package directory. It covers the relevant check
  types (e.g. spelling, changelog, README, snippets, linting, formatting, or all of them at once), and
  can auto-fix where supported. Consult the tool's parameters for the available check types and the fix
  option.
- `azsdk_package_run_tests` to exercise the package's tests when source code changed.

If the MCP tools are unavailable, fall back to the `azpysdk` CLI from the package directory (see
`doc/eng_sys_checks.md` for the full list of checks and how to run them). Check the package's
`pyproject.toml` to see which checks it opts in/out of, and scope checks to the changed packages only —
do not run the whole repo.

### 5. Report and gate the push

Summarize results as a concise table per check (PASS / FAIL, and the offending files/lines).

- **All pass** → tell the user it is safe to push.
- **Any fail** → do **not** advise pushing. Surface the specific failures and remediate:
  - Spelling: fix the typo, or if intentional add the word to the service-level
    `cspell.json`/`cspell.yaml`, or to `.vscode/cspell.json` for repo-wide terms, or an inline
    `# cspell:ignore <word>` for one-offs.
  - Links: fix the broken target; replace `.../blob/main/...` style links per the link guidance;
    add genuinely-unreachable-but-valid links to `eng/ignore-links.txt`.
  - SDK package failures: use the matching fix skills (`fix-pylint`, `fix-mypy`, `fix-sphinx`,
    `fix-black`) or `azsdk_package_run_check`'s fix option.
- Re-run only the checks that failed until green, then confirm the user can push.

## Notes

- Mirror CI exactly
- Keep it fast: only check changed markdown for links and only changed packages for SDK checks.
- Treat CSpell and Verify-Links as the default "non-SDK safety net" — always run them when any file
  changed, even if no SDK package was touched.
