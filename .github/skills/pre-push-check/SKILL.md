---
name: pre-push-check
description: Pre-push hook for azure-sdk-for-python. Before code is pushed, it analyzes the files changed against the target branch and runs the required CI checks locally so failures are caught before CI. Catches the easy-to-forget repo-wide checks (CSpell spelling and broken-link verification) for non-SDK changes, and runs the per-package SDK checks (pylint, mypy, pyright, cspell, changelog, etc.) via the azure-sdk-mcp tooling. Use before pushing/opening a PR.
---

# Pre-Push Check Skill

## Purpose

CI for this repo runs a mix of **repo-wide checks** and **per-package checks**. When working on
non-SDK code (docs, `.github/`, root markdown, samples, READMEs).

This skill emulates a pre-push hook: it figures out exactly what changed relative to the
target branch, runs only the checks relevant to those changes, and reports failures (with fixes where
possible) **before** the push so CI passes on the first try.

It prefers the `azure-sdk-mcp` `azsdk_package_run_check` / `azsdk_package_run_tests` tools for
per-package checks, and uses the repo's PowerShell scripts for the repo-wide checks that the MCP
tooling does not cover.

## When to use

- The user is about to `git push` or open a PR and wants to avoid CI failures.
- The user explicitly asks to run checks locally or validate changes.
- After making non-SDK edits (docs, eng, `.github`, READMEs) where spelling/link checks commonly fail.

## Prerequisites

- `pwsh` (PowerShell 7+), `git`, and Node.js (`npx`) on PATH — required for the spelling and link scripts.
- For SDK package checks via MCP, the environment must be set up. If unsure, run `azsdk_verify_setup` first.

## Steps

### 1. Determine the target (base) branch

The CI spell/link checks diff against the PR target branch using a **three-dot** diff
(`target...source`), matching `Get-ChangedFiles`. Determine the base ref:

- Default to `origin/main`.
- If the branch has an upstream that is not `origin/main`, ask the user which base the PR targets.
- Confirm the ref exists: `git rev-parse --verify <base>`.

Let `BASE` = the resolved target ref (e.g. `origin/main`) and `HEAD` = current branch.

> Tip: refresh remotes first so the comparison is accurate: `git fetch origin --quiet`.

### 2. Compute the changed files

Use the same three-dot diff the pipeline uses (excludes deleted files):

```bash
git diff "origin/main...HEAD" --name-only --diff-filter=d
```

Classify the changed files into:

- **SDK package changes** — paths matching `sdk/<service>/<package>/...`. Group by package
  directory (the directory containing `pyproject.toml` / `setup.py`).
- **Repo-wide / non-SDK changes** — everything else: `doc/`, `eng/`, `.github/`, root `*.md`,
  scripts, etc. These still flow through the repo-wide spelling and link checks.

If there are **no** changes vs the base, report that and stop.

### 3. Run the repo-wide checks (always, when there are changes)

These run on every PR regardless of which files changed and are the ones most often forgotten on
non-SDK work. Run them from the repo root.

**3a. CSpell — spelling on changed files**

```bash
pwsh -NoProfile -File eng/common/scripts/check-spelling-in-changed-files.ps1 \
  -SourceCommittish HEAD \
  -TargetCommittish origin/main \
  -ExitWithError
```

- Uses `.vscode/cspell.json` by default (plus any service-level `cspell.json`/`cspell.yaml`).
- `-ExitWithError` makes it exit non-zero on spelling errors (CI fails the PR, so mirror that here).

**3b. Verify-Links — broken / non-compliant links on changed markdown**

Only check the markdown files that changed (full-repo recursion is slow and unnecessary pre-push):

```bash
pwsh -NoProfile -Command '
  $md = git diff "origin/main...HEAD" --name-only --diff-filter=d |
        Where-Object { $_ -match "\.md$" }
  if (-not $md) { Write-Host "No changed markdown files."; exit 0 }
  ./eng/common/scripts/Verify-Links.ps1 `
    -urls $md `
    -recursive:$false `
    -checkLinkGuidance $true `
    -localBuildRepoName "Azure/azure-sdk-for-python" `
    -localBuildRepoPath (Get-Location).Path
'
```

- `-checkLinkGuidance $true` catches the common CI failures: disallowed relative links and links that
  hard-code the `main` branch (see https://aka.ms/azsdk/guideline/links).
- Network link checks can be slow or flaky; transient 403/timeout on external hosts are usually not
  the failure to fix — focus on `404`/host-not-found and guidance violations. The script exits
  non-zero when it finds genuinely broken links.

### 4. Run the per-package SDK checks (for each changed SDK package)

For every distinct changed SDK package directory, prefer the **azure-sdk-mcp** tooling:

- `azsdk_package_run_check` with `packagePath` = the package directory and `checkType`:
  - `Cspell` — package-scoped spelling.
  - `Changelog` — required changelog entry for the current version.
  - `Readme` — README validation.
  - `Snippets` — README/sample snippet validation.
  - `Linting` / `Format` — lint and formatting.
  - `All` — run the full set in one call (good default).
  - Pass `fixCheckErrors: true` to auto-fix where the tool supports it.
- `azsdk_package_run_tests` to exercise the package's tests when source code changed.

If the MCP tools are unavailable, fall back to the `azpysdk` CLI from the package directory
(see `doc/eng_sys_checks.md`). The release-blocking / most common static checks:

```bash
cd sdk/<service>/<package>
azpysdk pylint .
azpysdk mypy .
azpysdk pyright .
azpysdk verifytypes .
azpysdk sphinx .
azpysdk bandit .
azpysdk black .        # only if the package opts in (black = true in pyproject.toml)
```

Scope checks to the changed packages only — do not run the whole repo.

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
    `fix-black`) or `azsdk_package_run_check` with `fixCheckErrors: true`.
- Re-run only the checks that failed until green, then confirm the user can push.

## Optional: wire as a real git pre-push hook

To get a reminder automatically on `git push`, add an executable `.git/hooks/pre-push` that prompts
the user to run this skill (a git hook cannot invoke the agent directly, so it just reminds):

```sh
#!/bin/sh
echo "Reminder: run the 'pre-push-check' Copilot skill to validate CSpell, links, and changed SDK packages before pushing."
```

(`.git/hooks/` is local-only and not committed.)

## Notes

- Mirror CI exactly: use the three-dot diff against the PR target branch and `.vscode/cspell.json`.
- Keep it fast: only check changed markdown for links and only changed packages for SDK checks.
- Treat CSpell and Verify-Links as the default "non-SDK safety net" — always run them when any file
  changed, even if no SDK package was touched.
