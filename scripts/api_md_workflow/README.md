# API.md Workflow Helpers

This folder contains the helper scripts used by the GitHub Actions workflows that validate and update `API.md` files for changed SDK packages.

## Purpose

The workflow has two goals:

1. Detect when a pull request changes one or more SDK packages and the committed `API.md` files are out of date.
2. Allow the PR author or maintainer to re-run the workflow so the regenerated `API.md` files are committed back to the PR branch.

The logic is split between GitHub workflow YAML files and these Python helper scripts.

## Workflow Files

### `.github/workflows/consistency.yml`

This is the main workflow.

It runs on pull requests for changes under `sdk/**` and contains two jobs:

1. `consistency`
   - Detects affected package directories from the PR diff.
   - Regenerates `API.md` for those packages.
   - Fails if the generated files differ from the committed files.
   - Fails if an affected package does not have a committed `API.md`.
   - Uploads two artifacts:
     - `api-md-context`: package paths and mismatched files for rerun/apply
     - `api-md-comment`: JSON payload used by the commenter workflow

2. `apply-updates`
   - Only runs on reruns (`github.run_attempt > 1`).
   - Downloads `api-md-context` from the earlier job.
   - Regenerates `API.md` again.
   - Commits and pushes the updated files back to the same PR branch.
   - Posts a follow-up result comment to the PR.

### `.github/workflows/commenter.yml`

This is the trusted follow-up workflow.

It runs on `workflow_run` for `API.md Consistency` and does not build or regenerate code. It only:

1. Downloads the `api-md-comment` artifact from the completed consistency run.
2. Creates or updates a single PR comment using a marker-based upsert.

This separate workflow keeps comment publishing isolated from the PR execution context.

## Script Layout

### `common.py`

Shared helpers used by the other scripts:

- repository root resolution
- subprocess execution
- reading/writing line-based artifact files
- writing GitHub Actions outputs
- GitHub REST API helpers for listing/updating comments

### `find_affected.py`

Used by the `consistency` job.

Reads `API_MD_BASE_REF`, compares the PR branch to `origin/<base>`, and writes:

- changed package directories to `API_MD_CHANGED_FILE`
- valid package roots to `API_MD_PACKAGES_FILE`

Also writes `count=<n>` to `GITHUB_OUTPUT`.

### `regenerate.py`

Reads package directories from `API_MD_PACKAGES_FILE` and runs `scripts/generate_api_text.py` for each package.

This script is used in both:

- the initial consistency check
- the rerun apply step

### `find_mismatches.py`

Reads package directories from `API_MD_PACKAGES_FILE`, checks whether `<package>/API.md` is missing, untracked, or differs from git, and writes the mismatched file list to `API_MD_MISMATCHES_FILE`.

Also writes `mismatch_count=<n>` to `GITHUB_OUTPUT`.

### `build_comment_payload.py`

Builds the JSON payload consumed by `commenter.yml`.

Inputs come from environment variables such as:

- `PR_NUMBER`
- `REPOSITORY`
- `RUN_ID`
- `RUN_ATTEMPT`
- `CHANGED_COUNT`
- `MISMATCH_COUNT`

It writes the final comment JSON to `API_MD_COMMENT_FILE`.

The payload includes:

- a stable marker comment
- the PR number
- the rendered markdown body

When drift is found on the initial run, the body tells the user to open the workflow run and click `Re-run all jobs`.

### `build_apply_result_payload.py`

Builds the JSON payload for the follow-up comment after `apply-updates` runs.

It uses environment variables such as:

- `COMMIT_CREATED`
- `PR_NUMBER`
- `HEAD_REF`
- `RUN_URL`
- `COMMIT_SHA`

It writes the result payload to `API_MD_APPLY_RESULT_FILE`.

### `post_comment.py`

Posts or updates the PR comment from a payload file.

Inputs:

- `COMMENT_FILE`
- `GITHUB_TOKEN`
- `GITHUB_REPOSITORY`
- optional `DEFAULT_PR_NUMBER`
- optional `DEFAULT_MARKER`

Behavior:

1. Reads the JSON payload.
2. Finds an existing bot comment containing the same marker.
3. Updates that comment if found, otherwise creates a new one.

This is used by:

- `commenter.yml` for the main consistency comment
- `consistency.yml` for the apply result comment

## Environment Variables Used

The scripts are intentionally simple and read inputs from environment variables set by the workflow steps.

Common variables include:

- `API_MD_BASE_REF`
- `API_MD_PACKAGES_FILE`
- `API_MD_CHANGED_FILE`
- `API_MD_MISMATCHES_FILE`
- `API_MD_COMMENT_FILE`
- `API_MD_APPLY_RESULT_FILE`
- `PR_NUMBER`
- `REPOSITORY`
- `RUN_ID`
- `RUN_ATTEMPT`
- `GITHUB_TOKEN`
- `GITHUB_REPOSITORY`

## End-to-End Flow

1. A PR changes files under `sdk/**`.
2. `consistency.yml` runs.
3. `find_affected.py` determines which packages were touched.
4. `regenerate.py` rebuilds `API.md` for those packages.
5. `find_mismatches.py` records any `API.md` drift, including missing or untracked `API.md` files.
6. `build_comment_payload.py` creates a comment artifact.
7. `commenter.yml` downloads that artifact and runs `post_comment.py`.
8. The PR comment tells the user to rerun the workflow if they want the fixes applied.
9. On rerun, the `apply-updates` job in `consistency.yml` runs.
10. It regenerates the files again, commits them, and posts a result comment via `build_apply_result_payload.py` and `post_comment.py`.

## Maintenance Notes

- Keep comment rendering logic in the Python scripts, not inline in the YAML.
- Keep workflow YAML focused on orchestration: checkout, setup, artifacts, and calling scripts.
- If the comment format changes, update the marker handling carefully so existing PR comments continue to be updated instead of duplicated.
