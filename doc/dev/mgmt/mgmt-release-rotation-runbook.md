# Python management SDK release rotation runbook

Use this runbook during the weekly Go/JavaScript/Python directly responsible
individual (DRI) rotation. It covers generated `azure-mgmt-*` release PRs, from
triage through release follow-up. Route handwritten SDK or generator changes to
the Python owner.

**Contacts:** the **service team** is the submitter/contact in the PR or linked
release plan. The **Python owner** is a management SDK maintainer listed under
`/**/*mgmt*/` in [CODEOWNERS](../../../.github/CODEOWNERS)
(currently @ChenxiJiang333, @msyyc, and @Azure/azure-arm-sdk-reviewers).
Ask the Python owner to coordinate generator, engineering-system, or vendor support.
Rotation assignment does not grant repository, CODEOWNER, or release permissions.

## 1. Find PRs needing attention

Use these live GitHub queries; open each PR for its current status.

| Queue | Purpose |
| --- | --- |
| [All open management AutoPRs](https://github.com/Azure/azure-sdk-for-python/pulls?q=is%3Apr+is%3Aopen+%22%5BAutoPR+azure-mgmt-%22+in%3Atitle) | Includes drafts and PRs without release/review labels. Start here. |
| [Review queue](https://github.com/Azure/azure-sdk-for-python/pulls?q=is%3Apr+is%3Aopen+label%3Amgmt-review-needed+draft%3Afalse) | Review requested; not proof that checks or human review are complete. |
| [Approved release candidates](https://github.com/Azure/azure-sdk-for-python/pulls?q=is%3Apr+is%3Aopen+%22%5BAutoPR+azure-mgmt-%22+in%3Atitle+label%3Aauto-release+draft%3Afalse+review%3Aapproved) | Check for merge blockers and hand off to the service team. Do not add duplicate approval. |
| [Held release PRs](https://github.com/Azure/azure-sdk-for-python/pulls?q=is%3Apr+is%3Aopen+%22%5BAutoPR+azure-mgmt-%22+in%3Atitle+label%3AHoldOn) | Wait for the planned window or the owner's decision. |
| [Recently merged release PRs](https://github.com/Azure/azure-sdk-for-python/pulls?q=is%3Apr+is%3Amerged+%22%5BAutoPR+azure-mgmt-%22+in%3Atitle+label%3Aauto-release+sort%3Aupdated-desc) | Follow up on publishing for this rotation's packages. Merged does not mean released. |

`mgmt-review-needed` requests automated review when applied.
`auto-release` opts changed packages into post-merge release.
Neither label is approval; either can remain on a draft or an already reviewed PR.
An updated timestamp can reflect bot activity, not a recent service-team response.

| Current state | Next action |
| --- | --- |
| Draft | Ask the service team to complete release prerequisites and mark the PR ready when intended. Do not mark it ready on their behalf. |
| `HoldOn`, `blocking-release`, or an explicit human hold | Keep the hold. Ask the person who owns it what must change before proceeding. |
| CI queued/running | Wait for the current revision's checks. Ask the Python owner about stuck or missing pipelines. |
| CI failed | Read the existing failure analysis and route the stated fix to the service team or Python owner. Do not restart review instead of fixing CI. |
| Ready, no valid approval | Continue with sections 2 and 3. |
| Approved, not merged | Identify the actual merge blocker or ask the service team to merge through its release plan. |

## 2. Check readiness and the automated review

Read the PR description, release plan, latest human decisions, and current checks.
Confirm the service team intends to release the listed package, SDK version, and
API version. Follow the linked
[SDK release prerequisites](https://eng.ms/docs/products/azure-developer-experience/develop/sdk-release/sdk-release-prerequisites).
A bot-created PR is not itself a release request.

Find the latest **Management SDK PR review** comment from the
[Python review workflow](../../../.github/workflows/mgmt-sdk-pr-review.md).
Check that its pinned evidence covers the current changes. An older complete
comment does not cover a later push.

| Review result | Reviewer action |
| --- | --- |
| Complete, no findings or unverified checks | Use the completed checks and evidence; do not reconstruct them. Continue with human review below. |
| Blocking findings | Ask the service team to make the listed source/configuration fixes and regenerate. Route emitter/generator issues to the Python owner. |
| Warning or suggestion | Read the finding and record its fix or justified disposition. Ask the Python owner when Python-specific judgment is needed. |
| Unverified checks, incomplete review, partial breaking-change attribution, or missing evidence | Ask the Python owner to complete or resolve the missing review. Missing evidence is not a pass. |
| Missing or stale result | If authorized, request a fresh analysis by applying `mgmt-review-needed`. If it is already present, remove and reapply it only when no review is active. Otherwise ask the Python owner. |

The workflow runs on the label event, not every subsequent push. Manual workflow
dispatch is disabled by default; it is not the rotation's fallback.

The workflow checks Python package versions, preview/stable metadata, client
consistency, README usage, and API-version drift. Its
[management review rules](../../../.github/instructions/reviewer/management.instructions.md)
define the scope. Do not repeat completed checks or review every generated model,
operation, sample, and test.

**Human review still covers:**

- Breaking changes and their disposition. **TypeSpec/API** attribution explains
  origin; it does not approve the break. Ask the service team to confirm intended
  service changes. Send generator/migration changes, unclear attribution, and
  exceptions to the Python owner. A major version bump alone is not permission.
  Use the [breaking-change guide](sdk-breaking-changes-guide.md) for known patterns.
- Outstanding Copilot and human review comments. Ask for real defects to be fixed
  upstream; record a reason when a suggestion does not apply. Do not require
  output-only edits to satisfy a generated-code suggestion.
- First-release onboarding not covered by the result: confirm required namespace
  approval, ownership, and a release pipeline with the Python owner. For a
  confirmed first release, a client-name finding requires `client.tsp`
  customization and regeneration, not a hand edit to `_client.py`.

## 3. Approve or re-approve

Approve only if you are an authorized reviewer, the service team has confirmed
readiness, current required CI passes, review findings have justified
dispositions, and no unresolved review, evidence gap, or hold remains.
The automated comment is advisory; it never grants human approval.

After a push or regeneration, inspect what changed since the previous approval.
Check the current GitHub review decision and branch requirements, not just an old
**Approved** event in the conversation. A previous approval can remain visible
while GitHub still requires review.

Recheck changed versions, changelog, API versions, customizations, and any affected
findings. Request fresh automated analysis when its evidence is stale, and wait
for current CI. Re-approve only after reviewing the new changes; do not blindly
repeat approval. If the current approval is still valid, do not add another one.
Route API-version changes after approval or unclear generated changes to the
Python owner.

## 4. Hand off merge and follow the release

Tell the service team when review is complete and point to its release plan's
next action. The service team normally merges; an authorized DRI may help only
when the service team requests it and all branch requirements are satisfied.
Never bypass required reviews, checks, or holds.

**Treat merge of an `auto-release` PR as a publishing action.** Confirm release
intent and timing before merge. The
[release template](../../../eng/pipelines/templates/stages/archetype-python-release.yml)
uses internal post-merge CI on `main` to select changed, declared package artifacts.
This automatic path does **not** wait for the manual `package-publish` approval
gate. Do not merge early assuming another approval will stop publication.

After merge, locate `python - <service-directory>` in the
[internal Python pipelines](https://dev.azure.com/azure-sdk/internal/_build?view=folders)
and find the run for the merged commit. Check `AutoReleasePrepare` and the target
package's `Release: <artifact>` stage. Confirm the exact version is available on
[PyPI](https://pypi.org/) and check the linked release plan's status.
Release-plan completion can fail separately from publication; do not republish
an existing version to repair tracking.

If publishing is absent, skipped, failed, or unclear, send the PR, package/version,
merged commit, pipeline link, and failed/skipped stage to the Python owner.
A missing `auto-release` label or artifact mapping can leave no automatic release.
Adding the label after the run is not a reliable recovery. Check for an active run
or an already published version before any retry.

For an intentional manual release, let the Python owner coordinate the
[unified release process](../release.md#releasing-through-unified-pipelines).
Only authorized release approvers validate and approve the intended package's
artifacts. Do not queue a second release by default, approve unrelated packages,
or upload manually with `twine`.

## 5. Common partner questions and escalation

| Question or symptom | Response / owner |
| --- | --- |
| "CI is green. Can you approve?" | Check readiness, the current automated result, breaking changes, and unresolved comments. Green CI alone is insufficient. |
| "You approved already. Can you approve again?" | Compare the new changes and current review requirements using section 3. Do not add duplicate approval when none is needed. |
| "Can you mark this draft ready or remove the hold?" | Ask the service team or hold owner to confirm readiness and timing. An approved draft is still a draft. |
| "Why did TypeSpec migration introduce breaking changes?" | Point to the attribution and breaking-change guide. Ask the Python owner to resolve unintended generator/migration breaks; do not accept them merely because code is generated. |
| "The first package has no pipeline / needs a different client name." | Ask the Python owner to coordinate onboarding or pipeline preparation. The service team fixes naming in `client.tsp` and regenerates. |
| "Playback tests fail after the API version changed." | Route recording updates to the service team with the existing failure analysis and [management test guide](tests.md). Do not hand-edit recordings or disable tests to obtain green CI. |
| "The PR merged. Where is the package?" | Inspect the post-merge release run and PyPI using section 4. Escalate the exact failed stage, not a request for another PR approval. |

Historical examples inspected on 2026-10-23 illustrate these distinctions:
[an approved draft](https://github.com/Azure/azure-sdk-for-python/pull/48930),
[an older approval with review still required](https://github.com/Azure/azure-sdk-for-python/pull/49633),
[a corrected first-release naming blocker](https://github.com/Azure/azure-sdk-for-python/pull/49457),
and [approval followed by a service-team merge/release handoff](https://github.com/Azure/azure-sdk-for-python/pull/48686).
These examples are not the live queue.

## 6. US-based coverage and rotation handoff

US-based colleagues can triage the queue, relay existing findings, request
service-team confirmation, and identify the next owner while Python maintainers
are offline. Authorized rotation reviewers can approve ordinary cases after the
checks above. Geography does not grant or restrict approval authority.

Do not give courtesy approvals, grant breaking-change exceptions, clear holds,
or merge early to bridge a time-zone gap. Do not regenerate packages, patch
generated output, rerun every check, or repeat completed automated analysis merely
to show progress. Use the Python owner for unresolved Python-specific decisions;
keep the blocker visible rather than substituting an uninformed approval.

Leave one clear next action in the existing PR thread. At handoff, give the next
DRI the PR link, package/version, current blocker, responsible owner, required
action, and release deadline or planned window. Include the release run if merged.
Never hand off "approved" as a substitute for verified release completion.
