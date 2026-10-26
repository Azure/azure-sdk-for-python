---
name: azsdk-python-mgmt-pr-triage
description: "Quickly list open Python management SDK AutoPRs for release rotators: automated review needs triggering, review already active, human review needed, changes after approval, and author follow-up after approval. Read-only; verify workflow activity before recommending a review trigger."
---

# Python management SDK PR triage

Use this skill when a rotator asks for management SDK PR queues, PRs needing
attention, or whether an automated management review is already active.
Follow the [release rotation runbook](../../../doc/dev/mgmt/mgmt-release-rotation-runbook.md)
for review and release decisions; this skill only helps find PRs.

## Prerequisites

- Python 3.10+ and authenticated GitHub CLI (`gh`) on PATH.
- Read access to repository contents, pull requests, and Actions runs.
- Read access to CODEOWNERS team membership when team owners apply.

No SDK installation or local repository checkout is needed to run the bundled
script. In Copilot, ask: **"Use azsdk-python-mgmt-pr-triage to show management SDK
PRs needing attention."** If skills are not available in the current client,
run the script directly.

## Run

```powershell
python <skill-dir>\scripts\triage_prs.py
```

Optional filters:

```powershell
python <skill-dir>\scripts\triage_prs.py --package azure-mgmt-iothub
python <skill-dir>\scripts\triage_prs.py --version 1.0.0b1
python <skill-dir>\scripts\triage_prs.py --repo Azure/azure-sdk-for-python --limit 500
```

Defaults: `Azure/azure-sdk-for-python`, at most 500 initially listed PRs, open
non-draft titles starting with `[AutoPR azure-mgmt-`. Include first releases.
Package and version filters are exact matches. Unknown versions are shown as
`unknown`; a version-filtered scan warns when it cannot classify a version.

## Report

Return the script's Markdown report and any diagnostic warnings, without
reinterpreting evidence as permission to approve or release. Preserve these
section numbers, omit empty sections, and sort each queue by most recently updated:

1. **Automated review needs triggering**: the bot review is missing or its
   linked run targets an older head, and no active review was detected.
   Recommend adding `mgmt-review-needed`, or removing/reapplying it when present.
2. **Automated review active**: link queued, requested, waiting, pending, or
   in-progress management review runs. Wait; do not request a duplicate,
   including when the active run targets an older revision.
3. **Human review needed**: no effective approval from applicable CODEOWNERS,
   or GitHub's review decision still requires review/changes.
4. **Changes after approval**: the current head differs from the effective
   approved commit. Inspect the changes and current review requirements;
   re-approve only if required.
5. **Author follow-up after approval**: link newer PR-author issue comments,
   inline review comments, or submitted review bodies. Read and respond or
   route the request; a comment does not itself require re-approval.

Entries include PR link, package/version, reason, and next action. A PR may
appear in multiple queues. CODEOWNERS use GitHub file precedence and the last
matching rule for changed package files at the PR's base commit. Resolve team
members and use each maintainer's latest opinionated review; a later ordinary
comment does not invalidate an approval.

## Evidence and limitations

- Query the management review workflow, not generic CI. Use its run's explicit
  `pull_requests` associations, not timestamps, title guesses, or `head_sha`
  alone (`pull_request_target` can use a base revision).
- Active runs without a PR association make activity verification incomplete.
  Show **Review activity unknown** and the run links; never recommend
  retriggering while activity cannot be verified.
- Identify the latest review comment by the GitHub Actions account, review
  heading, and workflow marker/footer. Check the linked run's workflow identity
  and associated PR head for freshness. An absent/unusable run link or head
  makes freshness unknown, not outdated. Incomplete bot results remain for
  human review; do not automatically rerun a current partial result.
- Activity is a point-in-time observation, not a lock. Follow the run link and
  confirm no review is active immediately before changing a label.
- Unknown ownership, inaccessible APIs, scan limits, changed PRs during
  collection, and missing version metadata produce explicit verification
  warnings. A partial scan must not claim that no PRs need attention.
- Exit code `0` means collection completed without verification warnings;
  `2` means the report is partial/unverified or collection failed. Read the
  report and stderr rather than treating an incomplete scan as an empty queue.

Never change labels, request reviews, post comments, approve, merge, or publish.
Holds, CI, release plans, release intent, and post-merge publication remain
manual runbook checks. Absence from a queue is not proof of release readiness.

## Development

Run fixture-based tests without GitHub access:

```powershell
python -m unittest discover -s .github\skills\azsdk-python-mgmt-pr-triage\tests -v
```
