---
name: create-api-review-pr
description: Create a GitHub PR for API review by comparing a baseline API surface against a target branch. Use this when the user wants to create an API review PR, compare API changes between versions, or review API surface differences for a package.
---

# Create API Review PR

Creates a dedicated API review PR that shows the diff between a baseline release and a target branch's API surface using `scripts/api_md_workflow/create_api_review_pr.js`.

## Prerequisites

1. The user must have `gh` CLI authenticated (`gh auth login`).
2. The working tree must be clean (no uncommitted changes).
3. Node.js must be installed.
4. `azpysdk` must be installed (`pip install -e ./eng/tools/azure-sdk-tools`).

## Information to Gather

Ask the user for the following using `vscode_askQuestions`:

### 1. Package Name (required)
The Azure SDK package name (e.g. `azure-storage-blob`, `azure-ai-projects`).

### 2. Baseline (optional)
The release tag to use as the baseline for comparison. Tags follow the format `<package-name>_<version>` (e.g. `azure-storage-blob_12.29.0`).

- If the user provides a package name and version separately, construct the tag as `<package-name>_<version>`.
- If this is a **new package** with no prior release, the baseline should be omitted (the script handles this as an empty baseline).

### 3. Target (optional)
The branch or PR to generate the "current" API surface from. Can be:
- A branch name (e.g. `main`, `feature-branch`) — fetched from `origin`
- An `owner:branch` reference (e.g. `someone:their-branch`) — fetched from the fork
- If omitted, defaults to `origin/main`

## Validation Steps

Before running the script:

1. **Validate the package exists**: Confirm a directory matching `sdk/*/<package-name>` exists with a `pyproject.toml` or `setup.py`.
2. **Validate the baseline tag** (if provided): Run `git tag -l "<tag>"` to confirm the tag exists. If the user provided a version like `12.29.0`, construct the full tag as `<package-name>_<version>` and validate that.
3. **Confirm the working tree is clean**: Run `git status --porcelain` and warn if there are uncommitted changes.

## Execution

Run the following command from the repository root:

```bash
node scripts/api_md_workflow/create_api_review_pr.js --package-name <package-name> [--base <tag>] [--target <target>]
```

### Examples

**Standard review (comparing a release tag to a PR branch):**
```bash
node scripts/api_md_workflow/create_api_review_pr.js --package-name azure-storage-blob --base azure-storage-blob_12.29.0 --target someone:feature-branch
```

**Review against main (no target specified):**
```bash
node scripts/api_md_workflow/create_api_review_pr.js --package-name azure-cosmos --base azure-cosmos_4.14.0
```

**New package (no baseline):**
```bash
node scripts/api_md_workflow/create_api_review_pr.js --package-name azure-keyvault-secrets --target main
```

## Post-Execution

The script will:
1. Generate `API.md` for both baseline and target
2. Push `base_<package>_<version>` and `review_<package>_<version>` branches
3. Open a draft PR (or print a compare URL if `gh pr create` fails)

Report the PR URL to the user when complete.
