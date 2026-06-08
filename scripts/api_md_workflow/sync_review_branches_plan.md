# Sync API Review Branches on Working Branch Push

## Goal

When a commit is pushed to a working branch and the API.md consistency check passes, discover every open API review PR associated with that working branch and trigger a sync pipeline for each matching review PR. Each sync pipeline compares the API artifacts from the working SHA that passed consistency with the same artifacts on the review branch, and updates the review branch only when those files differ.

The sync workflow must not blindly copy committed `api.md` or `api.metadata.yml` files from the working branch. Those files may be stale or incorrect, and the existing API.md consistency check may fail for the same commit. Review branches should only receive API artifacts after the API.md consistency workflow has passed for the working branch commit being synchronized, and only when the working branch artifacts differ from the same files on the review branch.

The workflow must support one working branch having multiple associated review branches, for example when the same SDK PR has API review PRs for multiple packages or versions.

## Current Branch Context

The current API review prototype already has most of the branch mechanics in `scripts/api_md_workflow/create_api_review_pr.js`:

- Review branches use `apireview/review_<package>_<version>` with suffixes such as `_a`, `_b`, etc. when multiple branches are needed.
- Baseline branches use `apireview/base_<package>_<version>`.
- Review branches are created from the selected base branch and then receive the generated target `api.md` and `api.metadata.yml` files.
- Existing review branches can be reused when their API state matches the desired generated output and, for review branches, the base branch is an ancestor.
- The generated review PR body records a human-readable working branch, working PR, or target tag reference.
- The generated review PR body already includes an invisible, machine-readable `api-md-review-sync` metadata block with the working branch, review branch, package, and base branch information.

## Proposed Design

Add two GitHub Actions workflows plus a small script layer under `scripts/api_md_workflow`:

1. **Dispatcher workflow.** Runs only after the API.md consistency workflow completes successfully for a working branch commit. For each package that passed consistency, it queries open PRs using the API review title convention, starting with `[API Review]`, that package name, and that package's working version. It then parses candidate PR metadata blocks and triggers one sync pipeline run for each package-specific review PR whose `workingOwner` and `workingBranch` match the checked working branch.
2. **Sync pipeline.** Runs once per matching review PR. It receives the working branch, review branch, package directory, and working SHA from the dispatcher. It compares `api.md` and `api.metadata.yml` at the working SHA with those same files on the review branch. If neither file differs, it exits successfully. If either file differs, it copies both API artifacts from the working SHA and commits them to the review branch.

The initial implementation should use the consistency-gated copy strategy. The sync pipeline does not regenerate API artifacts; it relies on the successful API.md consistency result to prove the committed artifacts on the working branch are current.

The main tradeoff in this design is discovery cost. Scanning open `[API Review]` PRs can be slow and may run into GitHub API rate or search quota limits if the number of open review PRs grows. The upside is operational simplicity: the repository does not need an external index or durable lookup table for working-branch-to-review-branch associations. An external index would make lookup more efficient, but it would introduce extra state, synchronization rules, backfill behavior, and failure modes.

Review PRs are package-specific, while a single working branch consistency run may validate multiple packages. The dispatcher must therefore run discovery per package that passed consistency, not once for the whole working branch. Each package gets its own title-filtered review PR search and metadata verification pass.

## Association Model

`create_api_review_pr.js` already writes a hidden metadata block into the review PR body. This keeps the association on the review PR itself, avoids creating repo-wide state files, and allows multiple review PRs to point back to the same working branch.

There is intentionally no metadata written on the working branch side, as it may not be associated with a GitHub PR or issue where metadata could be annotated. Since the initiating change happens on the working branch, discovery has to work in reverse: after the working branch passes consistency, search candidate API review PRs, parse the invisible machine-readable blocks stored there, and find the review PRs whose `workingOwner` and `workingBranch` point back to that working branch.

Existing block shape:

```markdown
<!-- api-md-review-sync
DO NOT MODIFY THESE CONTENTS!
{
  "schemaVersion": 1,
   "repository": "Azure/azure-sdk-for-python",
   "packageName": "azure-keyvault-keys",
   "packageDir": "sdk/keyvault/azure-keyvault-keys",
   "baseBranch": "apireview/base_azure-keyvault-keys_4.11.1",
   "reviewBranch": "apireview/review_azure-keyvault-keys_4.12.0b3",
  "workingOwner": "Azure",
   "workingBranch": "main",
   "workingPrNumber": null
}
-->
```

Use the `workingOwner` and `workingBranch` pair as the primary lookup key. `workingPrNumber` is not required for sync; it is only descriptive metadata when present.

The sync workflow should treat this block as read-only input. It should not create, rewrite, or repair metadata in review PR bodies.

## Dispatcher Workflow Steps

1. Ignore runs for `apireview/**` branches.
2. Run after the API.md consistency workflow completes successfully. The dispatcher should ignore unsuccessful, skipped, or cancelled consistency runs.
3. Resolve the working branch identity from the completed workflow run:
   - `workingOwner`: the owner of the workflow run's head repository.
   - `workingBranch`: the workflow run's head branch.
   - `workingSha`: the workflow run's head SHA, retained for logging and optional pinning.
4. Determine the package set that passed API.md consistency for the completed workflow run. Each package record should include at least `packageName`, `packageDir`, and working version.
5. For each package, query open PRs in `Azure/azure-sdk-for-python` using the API review title convention: `[API Review]`, that package name, and that package's working version.
6. Parse each candidate PR body for one hidden `api-md-review-sync` metadata block.
7. Select every PR whose metadata satisfies all of these checks:
   - `workingOwner` and `workingBranch` match the completed consistency run.
   - `packageDir` matches the package currently being processed.
   - `packageName` matches the package currently being processed.
8. For each matching PR, trigger a sync pipeline with the following data: `packageDir`, `reviewBranch`, `workingOwner`, `workingBranch`, and `workingSha`.
9. Summarize which review PRs triggered sync runs, if any. If none, say so.

## Sync Pipeline Steps

1. Accept workflow inputs from the dispatcher:
   - `packageDir`
   - `reviewBranch`
   - `workingOwner`
   - `workingBranch`
   - `workingSha`
2. Checkout the `workingSha` commit from the working owner and branch and read the `api.md` and `api.metadata.yml` files into memory.
3. Verify that `workingSha` is still the current head of `workingOwner`/`workingBranch`. If it is stale, exit successfully without updating the review branch.
4. Checkout the `reviewBranch` from `Azure/azure-sdk-for-python` and read the `api.md` and `api.metadata.yml` files into memory.
5. Diff the files. If there is no diff, exit successfully without committing.
6. If either file differs, copy both API files from the working branch to the review branch, commit the result, and push with `--force-with-lease`.
7. Summarize whether the review branch was already current, updated, skipped as stale, or failed.

## Concurrency

Use a dispatcher workflow concurrency group keyed by `workingOwner` and `workingBranch` with `cancel-in-progress: true`, so a newer commit on the same working branch cancels older in-flight dispatch work.

The sync pipeline should also verify that `workingSha` is still the current head of `workingOwner`/`workingBranch` before updating a review branch. If the working SHA is stale, the sync run should exit successfully without pushing.

## Permissions and Safety

The dispatcher workflow needs `pull-requests: read` to discover review PR metadata and `actions: write` to trigger sync pipeline runs. The sync pipeline needs `contents: write` to push review branch updates.

Safety checks should include:

- Ignore consistency runs for `apireview/**` branches.
- Only trigger sync runs after API.md consistency succeeds.
- Cancel older in-flight dispatcher runs for the same `workingOwner` and `workingBranch` when a newer commit starts dispatch.
- Only inspect open PRs whose title contains `[API Review]`, the current package name, and the current package's working version before reading PR bodies.
- Only trigger sync for review PR metadata whose `workingOwner`, `workingBranch`, `packageName`, and `packageDir` match the current package and completed consistency run.
- Before updating a review branch, verify that `workingSha` is still the current head of `workingOwner`/`workingBranch`.
- Only copy `api.md` and `api.metadata.yml` under the metadata-verified `packageDir`.
- Use `--force-with-lease`, never a plain force push.
- Never create new review branches from this sync workflow. Branch creation remains the job of `create_api_review_pr.js`.

## Testing Plan

Add Node unit tests for the new script helpers:

- Metadata parser accepts exactly one valid existing hidden block, including the `DO NOT MODIFY THESE CONTENTS!` line.
- Metadata parser ignores malformed or unrelated comments.
- Dispatcher derives every package that passed consistency and builds one title query per package from `[API Review]`, package name, and working version.
- Dispatcher selects only metadata whose `workingOwner`, `workingBranch`, `packageName`, and `packageDir` match the current package and completed consistency run.
- Dispatcher returns multiple package-specific review PRs for one working branch when applicable.
- Dispatcher triggers one sync pipeline run per selected review PR with `packageDir`, `reviewBranch`, `workingOwner`, `workingBranch`, and `workingSha`.
- Dispatcher reports packages with no matching review PRs.
- Sync comparison exits without a commit when neither API artifact differs between `workingSha` and `reviewBranch`.
- Sync comparison copies both API artifacts when either file differs.
- Sync exits successfully without pushing when `workingSha` is stale.

If practical, add lightweight integration-style tests with stubbed git, gh, and workflow-dispatch runners that verify the dispatcher handles multiple packages independently and the sync script copies only the two API files, skips the push when there is no diff, and updates one review branch independently from other matching review PRs.

## Recommended Implementation Order

1. Add metadata parsing, package derivation, and dispatcher selection tests.
2. Add sync comparison and branch-update tests.
3. Add `dispatch_review_branch_syncs.js` to derive packages, query candidate review PRs, verify metadata, and trigger sync runs.
4. Add `sync_review_branch.js` to compare artifacts at `workingSha` against `reviewBranch` and update the review branch when needed.
5. Add the consistency-gated dispatcher workflow with `pull-requests: read` and `actions: write`.
6. Add the per-review-PR sync workflow with `contents: write`.