# Publication evidence and follow-up

## Verify publication first

A build's `completed/succeeded` status does not prove publication. Inspect `Release_azureaievaluation`, publication tasks, and the exact version on PyPI:

```powershell
$release = Invoke-RestMethod 'https://pypi.org/pypi/azure-ai-evaluation/<version>/json'
$release.info.version
$release.urls | Select-Object filename, packagetype, yanked, upload_time_iso_8601
```

Replace `<version>` with the intended version. Require expected wheel (`bdist_wheel`) and source distribution (`sdist`) availability and inspect yanked state. A 404, missing distribution, or yanked artifact is not a clean successful release; investigate without automatically republishing.

Trace the built artifact back to the verified source SHA. Only describe a version as the "first fixed release" once it is published **and** includes the fix commit; a merged PR, release tag, or dated changelog alone is insufficient.

## Review the next-version PR

The release template creates **Increment version for evaluation releases**, with branch pattern `increment-package-version-evaluation-<build ID>`. Find the actual PR tied to the observed run; it may be absent if a later task failed.

Inspect its real diff and base/head. Expect `_version.py` and the next unreleased changelog entry to agree, leaving published notes/date intact. Validate the next version against repository classification rules and planned changes, rather than inventing a fixed minor/patch increment. Check scope, CI and human review before any user-authorized auto-merge arrangement; do not enable it or merge on the user's behalf.

Report publication and follow-up separately: a failed version-bump PR task does not undo an observed PyPI upload, and an increment PR is not proof the intended package was published.

## Exceptional hotfix process

The team's supplied hotfix convention is for critical security/breaking issues, not every patch-numbered release. Confirm applicability, current release owners, ASK MODE and Core SDK coordination before creating branches.

Start from the **actual published release tag**, using `hotfix/azure-ai-evaluation/<version>` as the team branch convention. Fix main first through an approved PR, then cherry-pick only the reviewed fix onto the hotfix branch. Any security/authentication changes require the repository's security review.

Only on that hotfix branch, remove an inapplicable future minor entry and set the hotfix version; never erase released history or change main's future-release entry to imitate the hotfix. Review compatibility, notes, checks, API/release approvals and publication evidence as for the normal route. The agent does not approve, merge, or publish. No auto-hotfix decision follows from the word "patch".
