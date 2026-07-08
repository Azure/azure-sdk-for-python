---
name: create-api-review-pr
description: Create a GitHub PR for API review by comparing a baseline API surface against a target tag or branch. Use this when the user wants to create an API review PR, compare API changes between versions, or review API surface differences for a package.
---

# Create API Review PR

Creates a dedicated API review PR that shows the diff between a baseline release and a target tag or branch's API surface using `scripts/api_md_workflow/create_api_review_pr.py`.

## Unsupported Requests

If the user asks to create an API review PR for a new package, explain that new packages do not use API review PRs and stop. Do not gather script inputs or run `create_api_review_pr.py` for new packages.

## Prerequisites

1. The user must have `gh` CLI installed and authenticated (`gh auth login`), or `GITHUB_TOKEN`/`GH_TOKEN` set with permission to create and update pull requests in this repository.
2. The working tree must be clean (no uncommitted changes).
3. Python 3.10 or later must be available.
4. `azpysdk` must be installed (`pip install -e ./eng/tools/azure-sdk-tools`).
5. ApiView stub generator dependencies must be installed (`pip install -r ./eng/apiview_reqs.txt`).
6. `azsdk` CLI may be needed for package work item lookup. Do not proactively check or install it before running `create_api_review_pr.py`; the script detects supported install locations and reports when installation or update is necessary.

## Information to Gather

Ask the user for the following using `vscode_askQuestions`:

### 1. Package Name (required)
The Azure SDK package name (e.g. `azure-storage-blob`, `azure-ai-projects`, `azure-servicebus`, `azure-planetarycomputer`).

### 2. Baseline (required)
The release tag to use as the baseline for comparison. Tags follow the format `<package-name>_<version>` (e.g. `azure-storage-blob_12.29.0`).

- If the user provides a package name and version separately, construct the tag as `<package-name>_<version>`.

### 3. Target (optional)
The branch or PR to generate the "current" API surface from. Can be:
- A package release tag (e.g. `azure-storage-blob_12.30.0`) — used directly as a tag ref
- A branch name (e.g. `main`, `feature-branch`) — fetched from `origin`
- An `owner:branch` reference (e.g. `someone:their-branch`) — fetched from the fork
- If omitted, defaults to `origin/main`

## Validation Steps

Before running the script:

1. **Validate the package exists**: Confirm a directory matching `sdk/*/<package-name>` exists with a `pyproject.toml` or `setup.py`.
2. **Validate the baseline tag**: Run `git tag -l "<tag>"` to confirm the tag exists. If the user provided a version like `12.29.0`, construct the full tag as `<package-name>_<version>` and validate that.
3. **Validate the target tag when applicable**: If the user provided a target version or tag, construct or validate the full tag as `<package-name>_<version>` and run `git tag -l "<tag>"`.
4. **Confirm the working tree is clean**: Run `git status --porcelain` and warn if there are uncommitted changes.

Do not proactively run `azsdk --help`, `azsdk package find-work-item --help`, or the `azure-sdk-mcp.ps1` installer as a validation step. If `create_api_review_pr.py` fails with an error saying the `azsdk` CLI is not found or the `package find-work-item` command is unavailable, then run `pwsh ./eng/common/mcp/azure-sdk-mcp.ps1` from the repository root to install or update it, and rerun the same `create_api_review_pr.py` command once. If the script still reports an `azsdk` error after that, stop and report the failure.

## Execution

This is a long-running operation. The script may take several minutes because it generates API surfaces for both the baseline and target, creates or reuses review branches, pushes branches, and then opens the draft PR. Do not treat quiet terminal periods during `apistub` generation as failure unless the command exits, prints an error, or waits for input.

If `create_api_review_pr.py` fails while running this skill, do not patch the script, modify package files, retry with workaround edits, or try to manually complete branch/PR creation. Stop the workflow, report the failure clearly, include the relevant error details, and suggest practical next steps.

If the script reports that there are no API differences, relay that message to the user and stop. Do not create branches or a PR manually.

Run the following command from the repository root:

```bash
python scripts/api_md_workflow/create_api_review_pr.py --package-name <package-name> --base <tag> [--target <target>]
```

### Examples

**Standard review (comparing a release tag to a PR branch):**
```bash
python scripts/api_md_workflow/create_api_review_pr.py --package-name azure-storage-blob --base azure-storage-blob_12.29.0 --target someone:feature-branch
```

**Release-to-release review (comparing two package tags):**
```bash
python scripts/api_md_workflow/create_api_review_pr.py --package-name azure-ai-projects --base azure-ai-projects_2.1.0 --target azure-ai-projects_2.2.0
```

**Review against main (no target specified):**
```bash
python scripts/api_md_workflow/create_api_review_pr.py --package-name azure-cosmos --base azure-cosmos_4.14.0
```

## Post-Execution

The script will:
1. Generate `api.md` for both baseline and target
2. Push `apireview/base_<package>_<version>` and `apireview/review_<package>_<version>` branches
3. Open a draft PR (or print a compare URL if `gh pr create` fails)

During execution, report progress at major phases: baseline generation, target generation, branch creation or reuse, branch push, and PR creation. If the terminal is quiet, check whether the process is still running before assuming it is hung.

When the target is a tag, the PR body labels it as `Target tag`. Branch and fork targets are labeled as `Working branch`.

Report the PR URL to the user when complete.
