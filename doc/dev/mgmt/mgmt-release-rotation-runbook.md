# Python management SDK release rotation runbook

This runbook is for Go/JavaScript/Python rotation reviewers who are unfamiliar
with Python SDK releases. It explains how to find a release PR, use the bot's
review, decide the next action, and follow the release. You do not need a local
Python environment or detailed knowledge of generated Python code for routine cases.
The reviewer on duty is the directly responsible individual (**DRI**). Ask the
Python owner to review handwritten SDK or code-generation tool changes.

Python management SDKs manage Azure resources and use package names such as
`azure-mgmt-network`. An **AutoPR** contains automatically generated SDK changes.
**CI** is the set of automated PR checks. A **release plan**, linked from the PR,
tracks the service team's release request. Released Python packages are published
to the Python Package Index (**PyPI**).

**Contacts:** the **service team** is the submitter/contact in the PR or linked
release plan. The **Python owner** is a management SDK maintainer listed under
`/**/*mgmt*/` in [CODEOWNERS](https://github.com/Azure/azure-sdk-for-python/blob/main/.github/CODEOWNERS).
Ask the Python owner to coordinate code-generation, pipeline, or vendor support.
Rotation assignment does not grant repository, CODEOWNER, or release permissions.

## 1. Find PRs needing attention

Start from one [management AutoPR queue](https://github.com/Azure/azure-sdk-for-python/pulls?q=is%3Apr+is%3Aopen+draft%3Afalse+%22%5BAutoPR+azure-mgmt-%22+in%3Atitle+sort%3Aupdated-desc).
It lists open, non-draft PRs, most recently updated first. Open each PR and check
for these three cases:

| Needs attention | Next action |
| --- | --- |
| No valid approval | Use the bot review and CI in section 2, then approve when ready. |
| New commits after approval | Inspect the changes and re-approve if required, using section 3. |
| New PR-author comments after approval | Read the request and respond or route it to the Python owner. A comment alone does not require another approval. |

GitHub search does not isolate commits or author comments after approval. Check
the PR timeline; bot activity also updates the sort order. The queue does not
filter by `mgmt-review-needed` or `auto-release`: neither label proves readiness.
Drafts are excluded; the service team must mark them ready when intended.
Keep `HoldOn`, `blocking-release`, and explicit human holds until the owner clears
them. If approval is current and no request needs a response, do not approve again.

## 2. Request and read the bot review

Confirm the service team's release intent in the PR or release plan, including the
package, SDK version, and API version. The service team owns the
[SDK release prerequisites](https://eng.ms/docs/products/azure-developer-experience/develop/sdk-release/sdk-release-prerequisites).

For routine review, focus on the bot comment and current CI:

1. Read the latest **Management SDK PR review** bot comment. If it is missing or
   outdated, ask an SDK maintainer to add `mgmt-review-needed`. This label triggers
   the [review workflow](https://github.com/Azure/azure-sdk-for-python/blob/main/.github/workflows/mgmt-sdk-pr-review.md).
   If the label is already present, remove and reapply it only when no review is
   active. Wait for the updated comment; ask the Python owner if none appears.
2. Follow the comment's findings and next actions. Ask the service team to resolve
   reported source/configuration issues. Send incomplete or unverified results,
   unclear breaking changes, and Python-specific decisions to the Python owner.
   Missing evidence is not a pass; the bot does not authorize breaking changes.
3. Check CI for the current revision. Wait for running checks. For failures, use
   the existing failure analysis and route the fix to the service team or Python
   owner. Do not restart review instead of fixing CI.
4. Once the findings and outstanding human comments are resolved, use section 3
   to approve. Do not repeat completed bot checks or inspect every generated file.

Leaving `mgmt-review-needed` on the PR does not request another review after a push.
Do not request another run while one is active.

## 3. Approve or re-approve

Approve only if you are an authorized reviewer, the service team has confirmed
readiness, current required CI passes, review findings have justified
dispositions, and no unresolved review, evidence gap, or hold remains.
The automated comment is advisory; it never grants human approval.

After new commits, inspect the changes since approval and request an updated bot
result when the previous result is outdated. Wait for current CI and resolve any
new findings. Ask the Python owner about API-version changes or unclear generated
changes. Re-approve only after reviewing the new changes and only if required by
the current GitHub review decision and branch requirements. An old **Approved**
event alone does not prove approval is current.

Read new PR-author comments even when approval remains valid. Respond to the
request or route it to the Python owner; do not add a duplicate approval.

## 4. Hand off merge and follow the release

Tell the service team when review is complete and point to its release plan's
next action. The service team normally merges; an authorized DRI may help only
when the service team requests it and all branch requirements are satisfied.
Never bypass required reviews, checks, or holds.

**Treat merge of an `auto-release` PR as a publishing action.** Confirm release
intent and timing before merge. The
[release template](https://github.com/Azure/azure-sdk-for-python/blob/main/eng/pipelines/templates/stages/archetype-python-release.yml)
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
[unified release process](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/release.md#releasing-through-unified-pipelines).
Only authorized release approvers validate and approve the intended package's
artifacts. Do not queue a second release by default, approve unrelated packages,
or upload manually with `twine`.

## 5. Common partner questions and escalation

| Question or symptom | Response / owner |
| --- | --- |
| "CI is green. Can you approve?" | Check readiness, the current automated result, breaking changes, and unresolved comments. Green CI alone is insufficient. |
| "You approved already. Can you approve again?" | Compare the new changes and current review requirements using section 3. Do not add duplicate approval when none is needed. |
| "Can you mark this draft ready or remove the hold?" | Ask the service team or hold owner to confirm readiness and timing. An approved draft is still a draft. |
| "Why did TypeSpec migration introduce breaking changes?" | Point to the attribution and [breaking-change guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/mgmt/sdk-breaking-changes-guide.md). Ask the Python owner to resolve unintended generator/migration breaks; do not accept them merely because code is generated. |
| "The first package has no pipeline / needs a different client name." | Ask the Python owner to coordinate onboarding or pipeline preparation. The service team fixes naming in `client.tsp` and regenerates. |
| "Playback tests fail after the API version changed." | Route recording updates to the service team with the existing failure analysis and [management test guide](https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/mgmt/tests.md). Do not hand-edit recordings or disable tests to obtain green CI. |
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
