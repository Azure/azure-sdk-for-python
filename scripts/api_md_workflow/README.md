# API Review PR Helper

This folder contains the standalone helper used to create API review pull requests from generated `api.md` files.

## Purpose

`create_api_review_pr.py` automates API review PR creation for a package by:

1. Generating baseline and target API markdown snapshots.
2. Creating or reusing dedicated baseline/review branches.
3. Creating or reusing a draft GitHub PR with the `api.md` diff.
4. Assigning the PR to API review architects resolved from `.github/ARCHITECTS`.
5. Updating PR body sync metadata so future automation can identify branch relationships.
6. Letting the API review pending workflow update the package ADO work item from PR events.

The API consistency workflow helpers live under `.github/workflows/src/api-md-consistency`.

## Inputs and Output

Required inputs:

- `--package-name`: package folder name, such as `azure-ai-projects`.
- `--base`: baseline package tag, required to match `<package-name>_<version>` and exist locally/remotely.

Optional inputs:

- `--target`: one of:
	- package tag (for static tag-to-tag reviews),
	- branch name on `origin`,
	- `owner:branch` fork branch reference.
- `--python` / `--runtime`: runtime executable used for `azpysdk apistub` generation.

Primary output:

- A draft PR URL representing baseline vs review branch `api.md` diff.

Secondary output:

- PR body sync metadata includes the package work item ID when available, so `.github/workflows/api-review-pending.yml` can synchronize `Custom.PendingAPIReviews` on PR open, close, and reopen events.
- Matching API review architects are requested as GitHub reviewers when a PR number is available.

## High-Level Flow

`create_api_review_pr.py` executes this logical sequence:

1. Validate environment and arguments.
2. Resolve package directory.
3. Capture baseline `api.md` + `api.metadata.yml` from `--base` tag.
4. Capture target `api.md` + `api.metadata.yml` from resolved target ref.
5. Exit early if baseline and target `api.md` are identical.
6. Resolve branch reuse or branch creation for baseline and review branches.
7. Fetch the package work item ID for working-branch sync metadata.
8. Create or reuse PR between baseline and review branches.
9. Ensure PR sync metadata block in PR body.
10. Request API review architects as PR reviewers.
11. Restore original local branch.

## Detailed Decision Paths

### 1) Target Resolution

`--target` resolution order and behavior:

- If target is omitted: use `origin/main`.
- If target looks like package tag and exists as tag: use tag.
- Else if target is plain branch and exists on `origin`: use `origin/<branch>`.
- Else if target is `owner:branch` and exists on fork: use `FETCH_HEAD`.
- Else: fail.

Implication for PR body labeling:

- Tag target: labeled as `Target tag` and called out as static tag-to-tag review.
- Branch target: labeled as `Working branch` or `Working PR` if a matching open PR exists.

### 2) API Snapshot Capture

For both baseline and target refs, the script overlays package files from that ref, then runs `azpysdk apistub --md --extract-metadata`.

Captured artifacts:

- `api.md` bytes (required).
- `api.metadata.yml` bytes (optional but expected for metadata hash checks).
- parsed package version from `_version.py` or `version.py`.

After each capture, the script resets package files in the working tree to avoid local drift.

### 3) API Difference Gate

Diff condition is intentionally narrow:

- If `base.api_md == target.api_md`: no branches or PR are created.
- Metadata-only differences do not trigger PR creation.

### 4) Branch Reuse vs Branch Creation

Branch naming convention:

- baseline: `apireview/base_<package>_<baseVersion>`
- review: `apireview/review_<package>_<targetVersion>`

Reuse logic:

- Enumerate existing remote branches with same prefix.
- Read branch state (`api.md`, `api.metadata.yml`, `apiMdSha256`).
- Reuse branch only when branch state matches desired state.
- For review branch, required ancestor must include selected baseline branch.

Creation logic:

- Baseline branch starts from `origin/main` and commits baseline `api.md`/metadata.
- Review branch starts from selected baseline branch and commits target `api.md`/metadata.
- Both are pushed with `--force-with-lease`.

### 5) PR Reuse vs PR Creation

If both branches are reused:

- Search for existing open PR matching baseline/review pair.
- If found, reuse PR and update body sync metadata block if stale.

Otherwise:

- Attempt draft PR creation via GitHub REST API.
- If creation fails, search for already-open PR as fallback.
- If fallback PR exists, reuse it.
- If no PR is found, log manual compare URL and diagnostics.

Whenever a PR is created or reused, the script attempts to request API review from matching architects before updating the package work item.

### 6) API Review Architect Assignment

The script resolves API review architects from `.github/ARCHITECTS` using the package directory path and CODEOWNERS-style matching.

Behavior:

- Matching `@user` owners are requested as GitHub reviewers.
- Matching `@org/team` owners are requested as GitHub team reviewers using the team slug.
- The PR author is removed from direct user reviewer requests because GitHub rejects self-review requests.
- If no architects match, or all direct reviewers resolve to the PR author, reviewer assignment is skipped with diagnostics.
- GitHub reviewer request failures are warnings; branch/PR creation and work-item sync continue.

## PR Body Sync Metadata

The PR body can include a hidden metadata block (`api-md-review-sync`) with:

- repository slug,
- package name and dir,
- baseline/review branch names,
- working branch owner/name,
- optional working PR number,
- optional package work item id.

Behavior:

- Existing stale sync block is replaced.
- Block is omitted for target-tag flows (no working branch to track).

## ADO Package Work Item Sync Flow

For working-branch sync flows, the script fetches the package work item before creating or reusing the API review PR:

1. Fetch package work item via:

```bash
azsdk package get-work-item --package-name <package-name> -o json
```

2. Extract the work item `id` and write it to PR body sync metadata as `packageWorkItemId`.

The `.github/workflows/api-review-pending.yml` workflow owns `Custom.PendingAPIReviews` updates. On API review PR `opened` or `reopened`, it appends the PR URL if missing. On `closed`, it removes the PR URL.

The workflow updates the work item with:

```bash
azsdk package update-work-item \
	--work-item-id <id> \
	--field "Custom.PendingAPIReviews=<newline-separated-urls>" \
	--multiline-fields-format "Custom.PendingAPIReviews=markdown"
```

Failure policy:

- Work item fetch failures set sync metadata `packageWorkItemId` to `ERROR`.
- PR flow still succeeds; the event-driven workflow skips the package work item update when `packageWorkItemId` is unavailable.

## Error Handling Strategy

Hard failures:

- dirty working tree,
- detached HEAD,
- invalid/missing base tag,
- unresolved target reference,
- missing required API artifact generation.

Soft failures (warning and continue):

- inability to request API review architects as PR reviewers,
- inability to update PR body sync metadata,
- inability to fetch package work item details,
- inability to update package work item pending review URLs,
- draft PR creation failure when existing PR fallback succeeds.

## Example Usage


Baseline tag vs fork working branch:

Release from main review (most common):

```bash
python scripts/api_md_workflow/create_api_review_pr.py \
	--package-name azure-ai-projects \
	--base azure-ai-projects_2.1.0 \
	--target main
```

```bash
python scripts/api_md_workflow/create_api_review_pr.py \
	--package-name azure-ai-projects \
	--base azure-ai-projects_2.1.0 \
	--target someuser:feature/api-changes
```

Tag-to-tag review (uncommon):

```bash
python scripts/api_md_workflow/create_api_review_pr.py \
	--package-name azure-ai-projects \
	--base azure-ai-projects_2.1.0 \
	--target azure-ai-projects_2.2.0
```
