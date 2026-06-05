# api.md Workflow Helpers

This folder contains the helper scripts used by the GitHub Actions workflows that validate and update `api.md` files for changed SDK packages.

## Purpose

The workflow validates that when a pull request changes one or more SDK packages, the committed `api.md` files are still up to date.
`api.md` content is diff-gated by this workflow, and `api.metadata.yml` must be committed alongside it.
The workflow also validates adapter-selected metadata fields, such as `apiMdSha256` and `parserVersion`, so metadata differences can affect pass/fail.

The logic is split between GitHub workflow YAML files and helper scripts in Python and JavaScript.

## Workflow Files

### `.github/workflows/api-consistency.yml`

This is the main workflow.

It runs on pull requests for changes under `sdk/**`.

- Detects affected package directories from the PR diff.
- Regenerates `api.md` for those packages.
- Fails if the generated files differ from the committed files.
- Fails if an affected package does not have a committed `api.md`.
- Prints the mismatched or missing packages and the `azpysdk apistub --md --extract-metadata <package-name> --dest-dir .` command needed to regenerate each `api.md` file from the repository root.

## Script Layout

### `common.js`

Shared helpers used by the other scripts:

- repository root resolution
- subprocess execution
- reading/writing line-based artifact files
- writing GitHub Actions outputs
- GitHub REST API helpers for listing/updating comments

### `find_affected.js`

Used by the `consistency` job.

Reads `API_MD_BASE_REF`, compares the PR branch to `origin/<base>`, and writes:

- changed package directories to `API_MD_CHANGED_FILE`
- valid package roots to `API_MD_PACKAGES_FILE`

Also writes `count=<n>` to `GITHUB_OUTPUT`.

### `regenerate.js`

Reads package directories from `API_MD_PACKAGES_FILE` and runs `azpysdk apistub --md --extract-metadata <package-name> --dest-dir <package-dir>` for each package from the repository root.

This script is used by the consistency check.

### `find_mismatches.js`

Reads package directories from `API_MD_PACKAGES_FILE`, checks whether `<package>/api.md` is missing/untracked or differs from git, and writes:

- mismatched files to `API_MD_MISMATCHES_FILE`
- missing files to `API_MD_MISSING_FILE`

Also writes `mismatch_count=<n>`, `missing_count=<n>`, and `issue_count=<n>` to `GITHUB_OUTPUT`.

`api.metadata.yml` is also required and selected metadata fields are mismatch-checked according to the active adapter.

### `create_api_review_pr.js` and adapters

API review PR creation now uses a shared JavaScript orchestrator with a language adapter boundary:

- `create_api_review_pr.js`: shared git/branch/PR orchestration logic.
- `adapters/python.js`: Python-specific package discovery, version parsing, and `api.md` generation.

This split allows the core workflow to be reused across other language repos while keeping generation behavior language-specific.

`create_api_review_pr.js` compares a baseline package release tag with a target API surface. The target can be a package release tag, an `origin` branch, or an `owner:branch` fork reference. When the target is a tag, the generated PR body identifies it as a target tag instead of a working branch.

Example comparing two package release tags:

```bash
node scripts/api_md_workflow/create_api_review_pr.js --package-name azure-ai-projects --base azure-ai-projects_2.1.0 --target azure-ai-projects_2.2.0
```

### `api_md_workflow.config.json`

Shared configuration for adapter selection across `api_md_workflow` scripts.

- `adapter`: default adapter name (for this repo: `python`)

Both `create_api_review_pr.js` and `find_affected.js` read this file for adapter selection.

## Environment Variables Used

The scripts are intentionally simple and read inputs from environment variables set by the workflow steps.

Common variables include:

- `API_MD_BASE_REF`
- `API_MD_PACKAGES_FILE`
- `API_MD_CHANGED_FILE`
- `API_MD_MISMATCHES_FILE`
- `API_MD_MISSING_FILE`

## End-to-End Flow

1. A PR changes files under `sdk/**`.
2. `consistency.yml` runs.
3. `find_affected.js` determines which packages were touched.
4. `regenerate.js` rebuilds `api.md` for those packages.
5. `find_mismatches.js` records any `api.md` drift, including missing or untracked `api.md` files.
6. If drift is found, the workflow fails and prints the affected packages plus the `azpysdk apistub --md --extract-metadata <package-name> --dest-dir .` command to regenerate each `api.md` file locally from the repository root.
