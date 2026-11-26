---
name: azsdk-python-mgmt-pr-triage
description: "List open Python management SDK AutoPRs for release rotators, recognize configured rotator approvals, separate holds and missing release-plan links, and automatically trigger verified missing or outdated reviews."
---

# Python management SDK PR triage

Use this skill when a rotator asks for management SDK PR queues, PRs needing
attention, or whether an automated management review is already active.
Follow the [release rotation runbook](../../../doc/dev/mgmt/mgmt-release-rotation-runbook.md)
for review and release decisions. This skill finds PRs and can trigger automated
reviews; it never approves or releases a package.

## Prerequisites

- Python 3.10+ and authenticated GitHub CLI (`gh`) on PATH.
- Read access to repository contents, pull requests, and Actions runs.
- Read access to CODEOWNERS team membership when team owners apply, except
  the optional `Azure/azure-arm-sdk-reviewers` lookup described below.
- Label write access for automatic review triggers.

No SDK installation or local repository checkout is needed to run the bundled
script. In Copilot, ask: **"Use azsdk-python-mgmt-pr-triage to show management SDK
PRs needing attention."** If skills are not available in the current client,
run the script directly.

## Run

```powershell
python <skill-dir>\scripts\triage_prs.py --apply-labels
```

In Copilot, use `--apply-labels` by default so the skill performs label updates,
not the reviewer. For an explicitly read-only request, omit `--apply-labels`.
The standalone script remains read-only unless this flag is supplied.

Optional filters (add `--apply-labels` when automatic triggers are wanted):

```powershell
python <skill-dir>\scripts\triage_prs.py --package azure-mgmt-iothub
python <skill-dir>\scripts\triage_prs.py --version 1.0.0b1
python <skill-dir>\scripts\triage_prs.py --repo Azure/azure-sdk-for-python --limit 500
```

Defaults: `Azure/azure-sdk-for-python`, at most 500 initially listed PRs, open
non-draft titles starting with `[AutoPR azure-mgmt-`. Include first releases.
Package and version filters are exact matches. Unknown versions are shown as
`unknown`; a version-filtered scan warns when it cannot classify a version.

Active workflow runs block duplicate triggers **regardless of age**. The
72-hour UTC creation-time window applies only to completed attempts. Recent
failed reviews are reported, not automatically retried for the same head.

Head updates are detected during each triage scan, not by a push-event workflow.
For eligible automation-authored PRs, add or remove/reapply the label once for a
head that has no current review, active run, recent completed attempt, or
recorded trigger. The PR's GitHub App author establishes automation eligibility;
git commit author names do not establish which app pushed a commit. Any head
update on an eligible
automation PR is reevaluated, including a maintainer's update.

The script records label requests by repository, PR number, and head SHA in
`~/.cache/azsdk-python-mgmt-pr-triage/requests.sqlite3`. Use `--state-file <path>`
to select another database. Atomic claims prevent repeat label writes across
scans sharing this file, including before GitHub exposes a newly triggered run.
Read-only scans do not create or update this file. Keep the same state file
between scans; separate machines do not share these pending-request claims.
Only PR identifiers, SHAs, and request status are stored; no credentials.
Failed or interrupted requests remain recorded for manual investigation rather
than an automatic retry.

## Rotation configuration

Maintain authorized rotator GitHub user logins in
[`rotators.json`](rotators.json), under `repositories` and the exact repository's
`rotators` list. Keep this list current when rotation assignments change.
Use `--config <path>` to select another configuration file. Missing or invalid
configuration stops the scan; configuration for another repository does not
apply. User logins are case-insensitive and do not include `@`.

Configured rotators' approvals count like CODEOWNER approvals for triage.
Configuration does not grant GitHub review, merge, or release permissions and
does not override GitHub's current review decision.

## Report

Return the script's Markdown report and any diagnostic warnings, without
reinterpreting evidence as permission to approve or release. Preserve these
section numbers, omit empty sections, and sort each queue by most recently updated:

1. **First review needed**: no effective approval from applicable CODEOWNERS
   or configured rotators,
   or GitHub's review decision still requires review/changes.
2. **Changes after approval and need review again**: the current head differs from the effective
   approved commit. Inspect the changes and current review requirements;
   re-approve only if required.
3. **Author follow-up after approval**: link newer PR-author issue comments,
   inline review comments, or submitted review bodies. Read and respond or
   route the request; a comment does not itself require re-approval.
4. **Automated review needs triggering**: the bot review is missing or its
   linked run targets an older head, and no active review, recent completed
   attempt, or recorded request prevents a new trigger for this head.
   Automatically add `mgmt-review-needed`, or remove/reapply it when present,
   in `--apply-labels` mode. Report verified actions, skips, and failures.
5. **Automated review active**: link queued, requested, waiting, pending, or
   in-progress management review runs of any age. Wait; do not request a
   duplicate, including when an active run targets an older revision.
6. **HoldOn PRs**: PRs labeled `HoldOn` or `blocking-release` appear only here,
   with approval and release-plan evidence. The hold owner must clear the hold.
7. **Invalid PRs without release-plan link**: show only PR links whose
   descriptions lack a recognized release-plan dashboard link with a numeric
   `releaseplan` identifier. Do not include PRs with a release-plan link.
8. **Approved but unmerged for over two months**: current effective approvals
   strictly older than two calendar months in UTC. Use the approval date, not
   PR creation or update time. Ask the service team about merge/release intent.

Entries include PR link, package/version, reason, and next action. A PR may
appear in multiple queues, except held PRs. Section 7 contains PR links only.
Current approvals without outstanding review requirements are omitted from
review-needed and automated-review queues; follow-ups and aged approvals can
still appear. CODEOWNERS use GitHub file precedence and the last
matching rule for changed package files at the PR's base commit. Resolve team
members and use each maintainer's latest opinionated review; a later ordinary
comment does not invalidate an approval.

If the `Azure/azure-arm-sdk-reviewers` membership lookup returns HTTP 403,
silently skip that team lookup and cache the failure for the scan. Keep
approvals from individually named CODEOWNERS and other readable teams. Use
GitHub's review decision for the first-review queue when a team-only approval
cannot be verified; do not claim an approval is missing solely because this
team is unreadable. Changes and author follow-ups after a team-only approval
cannot be classified unless the approver is also a verified maintainer or
configured rotator.
Other team errors and API failures still produce verification warnings.

## Evidence and limitations

- Query the management review workflow, not generic CI. Use its run's explicit
  `pull_requests` associations, not timestamps, title guesses, or `head_sha`
  alone (`pull_request_target` can use a base revision).
- Fetch workflow runs without status or creation-time filters using pagination,
  so transitions between statuses do not hide an active run. Keep active runs
  regardless of age, including during each pre-write refresh. Apply the
  72-hour UTC creation-time boundary locally only to completed attempts;
  do not use PR update times as run age. Keep recent completed runs as per-head
  attempt evidence, excluding `skipped` runs: unrelated label events can create
  entirely skipped workflows that did not attempt a review. Report failures for the current head without
  automatically retrying. A later successful attempt supersedes an earlier failure.
- Compare the initial listing's `updatedAt` with the first PR read, then check
  for changes again after collecting evidence. Reject changed snapshots rather
  than combine an old review decision with newer reviews.
- Active runs of any age without a PR association make
  activity verification incomplete. Show **Review activity unknown**, the run
  status and link, and explain that automatic triggers were withheld to avoid
  duplicates. An old unassociated active run still blocks automatic triggers;
  inspect the linked run rather than assuming it is safe to retrigger.
- Identify the latest review comment by the GitHub Actions account, review
  heading, and workflow marker/footer. Check the linked run's workflow identity
  and associated PR head for freshness. An absent/unusable run link or head
  makes freshness unknown, not outdated. Incomplete bot results remain for
  human review; do not automatically rerun a current partial result.
- Automatic triggers apply only to non-draft management AutoPRs authored by
  `azure-sdk-automation[bot]` with an Azure-owned source repository. Other authors
  are reported but their labels are not changed.
- Before each label write, collect a fresh PR snapshot, approval decision, and
  workflow activity. Skip changed PRs, holds, current approvals, active reviews
  of any age, recent completed attempts for this head, recorded label
  requests, unknown evidence, or unknown workflow identity. Claim the head in
  the local request database before writing. Recheck after label removal before
  reapplying. Activity is a point-in-time observation, not a cross-machine lock.
- Verify label presence after writing. Do not equate label presence with a
  successful review run. Failed or uncertain writes produce warnings and are
  never automatically retried; removal followed by failure can leave the label
  absent. Inspect the PR and runs before recovery.
- Unknown ownership, inaccessible APIs, scan limits, changed PRs during
  collection, and missing version metadata produce explicit verification
  warnings. A partial scan must not claim that no PRs need attention.
- Exit code `0` means collection completed without verification warnings;
  `2` means the report is partial/unverified or collection failed. Read the
  report and stderr rather than treating an incomplete scan as an empty queue.

Do not change labels other than `mgmt-review-needed`, request human reviews,
post comments, approve, merge, or publish. CI, release-plan contents, release
intent, explicit human holds outside labels, and post-merge publication remain
manual runbook checks. Link detection does not verify plan status or release
readiness. Absence from a queue is not proof of release readiness.

## Development

Run fixture-based tests without GitHub access:

```powershell
python -m unittest discover -s .github\skills\azsdk-python-mgmt-pr-triage\tests -v
```
