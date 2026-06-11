# API Approval Work Item Tracking and APIVIew Gating Flow

## Goal

When an API review PR is marked approved in GitHub, record the approved package version and API hash on the package's Azure DevOps work item. During the Python release process, extend the existing APIVIew gating flow so it first checks whether the release artifact's exact version and API hash were approved in the work item. If that new check passes, the package is approved. If it fails, fall back to the existing APIView approval check.

The approval record must be tied to the exact API surface, not only to the package name or review PR. If a new commit changes the API after approval, the previous approval must no longer satisfy the work-item approval path. If approval is revoked, the work item must stop advertising that API hash as approved.

## Terms

- **Review PR:** The GitHub PR created by `scripts/api_md_workflow/create_api_review_pr.py` for an `api.md` diff. The PR title starts with `[API Review]` and the PR body contains hidden `api-md-review-sync` metadata.
- **API hash:** The normalized API markdown SHA-256 stored in `api.metadata.yml` as `apiMdSha256`. This hash is produced by `eng/scripts/Extract-APIViewMetadata-Python.ps1` after removing parser metadata and normalizing trailing whitespace and line endings.
- **Approved API tuple:** The package name, major.minor release line, full package version, API hash, review PR number, review commit, and approval state recorded on the Azure DevOps package work item.
- **Major.minor release line:** The `MAJOR.MINOR` portion of the package version. Current ADO package work items are scoped to this release line, so one work item can contain approvals for multiple patch and beta versions such as `1.2.0b1`, `1.2.0b2`, and `1.2.0`.
- **APIVIew gating flow:** The current APIView approval check used by release validation, including the `Create-APIReview.ps1` GA release path that fails when APIView approval is required and not approved.
- **Package work item:** The Azure DevOps work item returned by `azsdk-cli package get-work-item` for the package being reviewed or released.

## Current Context

The API review PR workflow already creates package-specific review PRs and records machine-readable metadata in the PR body. Review PRs are associated with `packageName`, `packageDir`, `reviewBranch`, `workingOwner`, `workingBranch`, and optional `workingPrNumber`.

The API markdown pipeline writes `api.metadata.yml` beside `api.md`. For Python, `api.metadata.yml` includes `apiMdSha256`, calculated from normalized `api.md` content by `eng/scripts/Extract-APIViewMetadata-Python.ps1`.

The branch sync proposal in `sync_review_branches_plan.md` keeps review branches aligned with API artifacts from the working branch after API.md consistency passes. This proposal assumes that workflow, or an equivalent workflow, exists so the review PR head contains current API artifacts for the reviewed package.

The Python release stage already has APIVIew gating behavior. The new work-item version/hash check should hook into that same decision point as an additional approval path. It will eventually replace that path.

## Proposed Design

Use the Azure DevOps package work item as the durable approval ledger. GitHub review state remains the event source, but release readiness is decided by the ADO work item record.

Add two automation paths:

1. **Approval recorder.** Runs as a GitHub Actions workflow when a GitHub review is submitted, dismissed, or when an approved API review PR receives a new commit. It looks up the package work item with `azsdk-cli package get-work-item`, then writes, revokes, or supersedes the approved version/hash record.
2. **APIVIew gating flow.** Runs at the same place the release process currently checks APIView approval. It calculates the release artifact's normalized API hash, looks up the package work item with `azsdk-cli package get-work-item`, and treats the package as API-approved if the work item has an active approval for that exact version and hash. If the work-item check does not pass, it falls back to the existing APIView approval check. Eventually, that APIView fallback will be removed.

The check should calculate the hash from the release artifact, not from the source tree, so it verifies the exact package that is about to ship.

The approval logic is intentionally an OR:

1. If the package's major.minor work item contains an active approval for `(version, apiMdSha256)`, pass.
2. Otherwise, evaluate the existing APIVIew gating flow.
3. If APIView approval passes, pass.
4. If both checks fail, fail the existing APIVIew gating flow with details from both checks. The new review process should be favored over pointing service teams to APIView.

## Work Item Approval Record

The package work item needs a structured field or attachment that can represent current approval state for multiple patch and beta versions within the same major.minor release line. The GitHub review PR is the detailed approval history; the work item should not duplicate every approval, revocation, or supersession event. Assuming this simplifies the implementation and operational model, the work item should have one entry per full package version, updated to reflect the current approval state for that version.

The exact ADO field names should be owned by the `azsdk-cli` contract, but the minimum shape is:

```json
{
  "schemaVersion": 1,
  "packageName": "azure-example-package",
  "language": "python",
  "majorMinorVersion": "1.2",
  "apiApprovals": [
    {
      "version": "1.2.0b1",
      "apiMdSha256": "<normalized-api-md-sha256>",
      "state": "revoked",
      "reviewPullRequest": "https://github.com/Azure/azure-sdk-for-python/pull/12345",
      "reviewBranch": "apireview/review_azure-example-package_1.2.0b1",
      "reviewCommit": "<review-branch-head-sha>",
      "approvedBy": "<github-login>",
      "approvedAt": "2026-06-10T00:00:00Z",
      "lastUpdatedBy": "<github-login>",
      "lastUpdatedAt": "2026-06-12T00:00:00Z"
    },
    {
      "version": "1.2.0",
      "apiMdSha256": "<normalized-api-md-sha256>",
      "state": "approved",
      "reviewPullRequest": "https://github.com/Azure/azure-sdk-for-python/pull/23456",
      "reviewBranch": "apireview/review_azure-example-package_1.2.0",
      "reviewCommit": "<review-branch-head-sha>",
      "approvedBy": "<github-login>",
      "approvedAt": "2026-06-20T00:00:00Z",
      "lastUpdatedBy": "<github-login>",
      "lastUpdatedAt": "2026-06-20T00:00:00Z"
    }
  ]
}
```

An active release approval is the single entry for the release candidate's full `version` in the matching package and major.minor work item. The work-item side of the OR check passes only when that entry's `apiMdSha256` matches the release artifact and `state` is `approved`. If the entry is missing, has a different hash, or has any other state, the work-item check does not pass and the APIVIew gating flow falls back to APIView.

Older approval history and rationale should remain on the GitHub review PR, not be copied into the work item. When a newer API hash appears for the same full package version, leave the existing approved hash approved. A release built from the newer hash will fail the work-item side of the APIVIew gating flow because the hash does not match. Once the newer hash is approved, update that version's single work-item entry to the new approved hash. If the architect wants to revoke the previous approval, they can do that explicitly. Different patch or beta versions under the same major.minor work item should each have their own single current-state entry.

## CLI Contract

The repository automation should avoid hand-constructing ADO REST patches where possible. Proposed CLI surface:

```bash
azsdk-cli package get-work-item --package-name <package> --language python --major-minor-version <major.minor> --output json
azsdk-cli package approve-api --work-item-id <id> --version <version> --api-hash <hash> --review-pr <url> --review-commit <sha> --approved-by <github-login>
azsdk-cli package revoke-api-approval --work-item-id <id> --version <version> --api-hash <hash>
azsdk-cli package check-api-approval --work-item-id <id> --version <version> --api-hash <hash>
```

These CLI commands are the stable boundary so the release pipeline and GitHub workflow do not need to know ADO field details.

## Approval Recorder Flow

Run the recorder as a GitHub Actions workflow triggered by API review PR events:

```yaml
on:
  pull_request_review:
    types: [submitted, dismissed]
  pull_request:
    types: [synchronize]
```

Use `pull_request_review` events to record approval or revocation, and use `pull_request` `synchronize` events to detect new commits pushed after approval.

1. Confirm the PR is an API review PR by title convention and by presence of the hidden `api-md-review-sync` metadata block.
2. Parse the metadata block to resolve `packageName`, `packageDir`, and `reviewBranch`.
3. Checkout or fetch the reviewed PR head commit.
4. Read `<packageDir>/api.metadata.yml` and extract `apiMdSha256`.
5. Resolve the full package version from the package metadata at the reviewed commit and derive its major.minor release line.
6. Run `azsdk-cli package get-work-item` for the package, language, and major.minor release line.
7. If the GitHub review state is approved, create or update the full version's work-item entry with `apiMdSha256` and `state=approved`.
8. If the review is dismissed, changes requested, or otherwise no longer approved, update the full version's work-item entry to a non-approved state such as `revoked`.

The recorder should be idempotent. Replaying the same approved event should leave the work item in the same state. Replaying a dismissal should leave the approval absent or marked revoked.

The recorder should update ADO only when it can prove that the PR metadata package name, package directory, review branch, major.minor release line, full version, and API hash all agree. If any of those checks fail, it should fail loudly and leave the work item unchanged.

## New Commit After Approval

A new commit pushed to the review PR after approval must invalidate approval for the new API surface.

Recommended behavior:

1. The existing review-branch sync flow updates the review branch when a working branch commit changes `api.md` or `api.metadata.yml`.
2. A `pull_request` synchronization handler runs for API review PRs.
3. If the PR had an approved record for the previous head commit, compare the new head's `apiMdSha256` with the approved hash.
4. If the hash is unchanged, leave the full version's work-item entry as-is.
5. If the hash changed, leave the existing work-item entry unchanged. The old approved hash remains approved, and the newer hash is simply not approved yet.
6. The GitHub PR should visibly require re-approval through branch protection, a failing status check, or a comment/status from the recorder. A release built from the newer hash will fail the work-item check until the new hash is explicitly approved and written to the work item.

The key rule is that approval follows `(version, apiMdSha256)` within the package's major.minor work item, not the PR number. Package name is still part of the work item lookup and must match before any approval record is considered. A later commit with a different hash is a different approval target. A different patch or beta version in the same major.minor work item is also a different approval target. If GitHub branch protection dismisses approvals automatically when new commits are pushed, the recorder can consume that dismissal event. If branch protection does not dismiss approvals, the hash comparison still prevents stale approval from satisfying release.

## Approval Revoked

Approval can be revoked explicitly when a GitHub review is dismissed or implicitly when a later review changes the PR state away from approved.

Recommended behavior:

1. Listen for `pull_request_review.dismissed` and review states that remove approval.
2. Recompute or read the API hash for the review commit associated with the dismissed approval.
3. Run `azsdk-cli package get-work-item` to find the package work item.
4. Update the full version's work-item entry to `state=revoked` when its `apiMdSha256` matches the dismissed approval.
5. Record only the current approval state in the work item; the GitHub PR remains the source for rationale and discussion.

The work-item check should treat revoked, superseded, missing, stale, or ambiguous approval records as not approved. That result should not immediately fail release; it should fall through to the existing APIView approval check.

## APIVIew Gating Flow

Hook into the same code path that currently enforces APIView approval for release. The APIVIew gating flow extension should run before the existing APIView status result is used to fail the package.

1. Determine `packageName`, release `version`, major.minor release line, and the release artifact path from the existing package validation context.
2. Generate or extract the API markdown for the release artifact using the same normalization path used by API review.
3. Calculate `apiMdSha256` from the release artifact's normalized `api.md`.
4. Run `azsdk-cli package get-work-item --package-name <package> --language python --major-minor-version <major.minor> --output json`.
5. Check whether the major.minor work item has a single entry for the release artifact's full `version` whose `apiMdSha256` matches the artifact and whose `state` is `approved`.
6. If the work-item check passes, mark API approval as satisfied and skip the existing APIView approval failure path.
7. If the work-item check fails, run or use the existing APIView approval status check.
8. If APIView approval passes, mark API approval as satisfied.
9. If both checks fail, fail the existing APIVIew gating flow.

The APIVIew gating flow should emit a concise failure message that includes the package name, release version, calculated API hash, work-item approval result, and existing APIView approval result.

## Release Pipeline Placement

Do not add a separate release-blocking job that bypasses existing APIVIew gating behavior. Instead, add the new work-item check where release validation currently decides whether APIView approval is required and approved.

The current enforcement shape is in the API review validation flow: APIView status is processed into an approval result, then GA release validation fails when APIView approval is required and not approved. The new logic should preserve that structure and change the final decision from:

```powershell
if ($apiViewApprovalRequired -and !$apiViewStatus.IsApproved) {
    fail
}
```

to:

```powershell
$majorMinorVersion = Get-MajorMinorVersion -Version $version
$workItemHashApproved = Test-WorkItemApiApproval -PackageName $packageName -MajorMinorVersion $majorMinorVersion -Version $version -ApiHash $apiMdSha256

if ($apiViewApprovalRequired -and !$workItemHashApproved -and !$apiViewStatus.IsApproved) {
    fail
}
```

This keeps the existing APIVIew gating flow as the fallback path and avoids changing release behavior for packages that do not yet have work-item hash approval records.

## Failure Modes

- **No package work item found:** Fail the recorder. In release validation, treat the work-item check as not approved and fall back to the existing APIView approval check.
- **Work item update fails:** Fail the recorder. Do not treat GitHub approval as recorded until ADO update succeeds.
- **Missing `api.metadata.yml`:** Fail. The workflow cannot prove which API hash was approved.
- **Malformed PR metadata:** Fail the recorder and require the API review PR to be repaired or recreated.
- **Release hash not found in ADO:** Fall back to the existing APIView approval check. If APIView approval also fails, fail release with an actionable message that includes the exact major.minor line, full version, and hash.
- **ADO contains approved version but different hash:** Fall back to the existing APIView approval check. If APIView approval also fails, show both hashes and explain that the newer hash needs explicit approval before the work-item path can pass.
- **ADO contains approved hash but revoked/superseded state:** Fall back to the existing APIView approval check. If APIView approval also fails, show the recorded state.

## Safety Rules

- Only process PRs that are confirmed API review PRs by metadata, not title alone.
- Only trust `apiMdSha256` from the reviewed commit's `api.metadata.yml` when it was produced by the same normalization tool used by release validation.
- Never mark approval by package name alone.
- Never mark approval by version alone.
- Never treat major.minor approval as sufficient for a patch or beta release. The full version and API hash must match an active approval record inside the major.minor work item.
- Treat multiple entries for the same full version as invalid. The work item should contain one current-state entry per full version.
- Do not automatically revoke or supersede approval when the review PR head changes and the API hash changes. Leave the approved hash in place until a newer hash is explicitly approved or the architect explicitly revokes approval.
- Treat GitHub approval dismissal as revocation for the matching version/hash.
- Make release validation read-only except for telemetry/logging.
- Treat work-item lookup, parsing, or ambiguity failures as a failed work-item check, then fall back to the existing APIView approval check.
- Fail release only when API approval is required and neither approval path passes.

## Permissions and Secrets

The approval recorder needs GitHub read access to PR bodies and branches, plus credentials that allow `azsdk-cli package get-work-item` and the selected ADO update path to read and update package work items.

The release validation extension needs read access to package work items and enough artifact access to calculate the release API hash. If it updates a diagnostic field such as `lastCheckedApiHash`, it also needs ADO write access; otherwise it can be read-only.

## Testing Plan

Add unit tests for the recorder helpers:

- API review metadata parsing accepts valid hidden metadata and rejects unrelated PRs.
- Approval recorder extracts `apiMdSha256` and package version from the reviewed commit.
- Approved review creates or updates the full version's work-item entry with `state=approved` and the approved `apiMdSha256`.
- Dismissed review updates the matching full version's work-item entry to `state=revoked`.
- PR synchronization with unchanged hash preserves approval.
- PR synchronization with changed hash leaves the existing work-item approval unchanged and reports that the newer hash needs approval.

Add APIVIew gating flow tests:

- Gate passes when the work item contains an active approval for the exact version and hash, even if the existing APIView status is not approved.
- Gate passes when the work-item check fails but the existing APIView status is approved.
- Gate fails when the work item is missing and the existing APIView status is not approved.
- Gate fails when the version matches but the hash differs and the existing APIView status is not approved.
- Gate fails when the matching full version entry has a different hash, is revoked, or is otherwise not approved, and the existing APIView status is not approved.
- Gate falls back to APIView when the work item response is malformed.

Add pipeline tests or dry-run jobs that stub `azsdk-cli package get-work-item` and the ADO update call before enabling the gate as release-blocking.

## Open Questions

- Which exact ADO field or attachment should hold the structured approval record?
- Should `azsdk-cli package get-work-item` return API approval records directly, or should a separate `package get-api-approval` command own that shape?
- Should the recorder update the ADO work item directly from GitHub Actions, or should it call an internal service/CLI command that performs policy checks centrally?
- What exact state names should the work-item entry support beyond `approved`, such as `pending`, `revoked`, or `superseded`?
- Should the work-item hash check live directly in the existing APIView PowerShell helper, or in a separate helper called from the current APIVIew gating flow decision branch?

## Recommended Implementation Order

1. Define the `azsdk-cli` approval read/write contract and ADO storage shape.
2. Add script helpers under `scripts/api_md_workflow` to parse review metadata, read `api.metadata.yml`, resolve package version, and call the CLI.
3. Add the GitHub approval recorder workflow for approved and dismissed review events.
4. Add PR synchronization handling to revoke approval when an approved review PR receives an API-changing commit.
5. Extend the existing APIVIew gating flow decision to pass when either work-item hash approval or APIView approval passes.
6. Add tests for recorder state transitions and APIVIew gating flow pass/fail cases.