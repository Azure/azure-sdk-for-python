---
name: audit-sdk-docs
description: Use when the user wants to audit this repo's documentation and annotations for outdated references - broken relative links, dead in-repo GitHub URLs, and inline references to files/paths that no longer exist - then update or delete the stale docs so agents get accurate, current info. Skips the auto-generated sdk/ folder and centrally-synced eng/common. Triggers on phrases like "check docs", "audit documentation", "delete/update outdated docs", "keep docs up to date".
---

# Audit SDK Docs

Audit the Markdown / reStructuredText documentation of the Azure SDK for Python
repo for **outdated references**, then update or delete the stale content. Keeping
docs accurate, current, and self-consistent improves agent task success, because
agents read these docs (`AGENTS.md`, `.github/copilot-instructions.md`,
`.github/skills/`, `doc/dev/`, ...) to decide how to work in the repo.

This skill is **agent-maintained**: when you discover a new class of staleness or
a better detection heuristic, extend the scanner and this checklist.

## Rules

- **SKIP the `sdk/` folder** - it is auto-generated; its docs/annotations are not
  hand-maintained. The scanner excludes it by default.
- **Do NOT edit `eng/common*`** - those files are centrally synced from
  `azure-sdk-tools` and are overwritten by automation. The scanner excludes them.
- **DO NOT edit too many files at one time.** Fix the highest-confidence stale
  references in a small batch; report the rest as follow-ups rather than mass-editing.
- **Every candidate needs agent judgement.** The scanner reports *candidates*, not
  confirmed bugs. Many hits are legitimate and must be left alone:
  - **Placeholders**: `sdk/mypackage/azure-mypackage`, `sdk/contoso/azure-contoso`,
    `sdk/path-to-your-package/_version.py`.
  - **Generated output paths**: `conda/noarch`, `.../code_reports/latest/report.json`.
  - **Gitignored user files**: e.g. `testsettings_local.cfg`, which docs instruct
    users to create locally.
  - **Code-snippet noise**: tokens like `{{`, `or`, `name="krista"` that the
    Markdown-link / inline-code regexes matched by accident.

## Workflow

1. **Scan.** Run the bundled scanner (fast, single process, read-only):

   ```
   python .github/skills/audit-sdk-docs/scripts/check_outdated_docs.py
   ```

   With no arguments it audits the repo this script lives in. By default it scans
   repo-root-level `*.md`/`*.rst` files plus `doc/` and `eng/` (excluding `sdk/`,
   `eng/common*`, `node_modules`). Options:
   - `REPO_ROOT` positional to point at another clone.
   - `--scan-dir DIR` (repeatable) to override which dirs are walked.
   - `--include-sdk` to also scan the auto-generated tree (rarely wanted).
   - `--org` / `--repo` to match in-repo GitHub URLs for a different repo.

   It prints candidates grouped by kind:
   - `BROKEN_RELATIVE_LINK` - `[text](rel/path)` whose target is missing.
   - `DEAD_REPO_URL` - `github.com/<org>/<repo>/blob|tree/main/<path>` that no
     longer exists locally.
   - `MISSING_PATH_REF` - inline-code path like `eng/foo.yml` that does not exist.

2. **Judge each candidate.** Open the doc at the reported line and read the
   surrounding context. Discard placeholders, generated paths, gitignored files,
   and code snippets. For a genuine stale reference, find where the target *moved
   to* before editing:
   - `grep` the codebase for the referenced filename / variable to locate the
     current path (e.g. a moved config file).
   - `git log -- <old-path>` to find the PR that moved/removed it.

3. **Fix a small batch.** Update the reference to the correct current path, or
   delete the doc/section if the feature is truly gone. Prefer minimal, surgical
   edits. Point sample links at a package that still exists.

4. **Verify.** Re-run the scanner; confirm the fixed candidates disappear and no
   new ones were introduced. Show `git diff` of the edited docs.

5. **Report.** Summarize what was fixed and list remaining lower-confidence
   candidates (and why they were left) as follow-ups.

## Example findings

- `doc/dev/conda-builds.md` referenced `eng/conda_env.yml`; the file was moved to
  `conda/conda-recipes/conda_env.yml` (PR #31804 "Refactor Conda Pipeline"). Fixed
  the path; verified via `grep AZURESDK_CONDA_VERSION` +
  `eng/tools/azure-sdk-tools/ci_tools/conda/conda_functions.py`
  (`get_version_from_config` reads `conda/conda-recipes/conda_env.yml`).
- `doc/dev/mgmt/tests.md` linked a sample `conftest.py` under
  `sdk/advisor/azure-mgmt-advisor/tests/` whose `tests/` folder no longer exists.
  Repointed to `sdk/apimanagement/azure-mgmt-apimanagement/tests/conftest.py`.
