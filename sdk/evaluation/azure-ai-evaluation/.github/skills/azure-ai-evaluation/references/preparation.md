# Prepare the evaluation release

Run PowerShell commands from the repository root. Use a fresh, clean isolated branch from verified current upstream main, not a merged release branch or stale local `main`. Inspect remotes, refresh the intended baseline and preserve unrelated work.

## Establish facts before choosing a version

```powershell
git status --short
git remote -v
Get-Content .\sdk\evaluation\azure-ai-evaluation\azure\ai\evaluation\_version.py
Get-Content .\sdk\evaluation\azure-ai-evaluation\CHANGELOG.md -TotalCount 65
$published = Invoke-RestMethod 'https://pypi.org/pypi/azure-ai-evaluation/json'
$published.info.version
$published.releases.PSObject.Properties.Name
```

Use semantic version ordering, not the last enumerated string. Identify the published release tag/commit; compare merged changes since it, Chronus entries and README/samples. Inspect the published wheel/API when compatibility is disputed.

Apply repository rules: bugfix patch, feature minor, breaking change major. Removing/reverting a **published** option can break compatibility even if `**kwargs` accepts and ignores it. Never hide breaking notes or treat readiness as a waiver. Stop on classification conflicts pending authorized reviewers; verify explicit exceptions.

Inspect an existing PyPI target first: versions cannot be overwritten. Agree on a new classified version if changes remain.

## Collect pending notes separately

`Prepare-Release.ps1` does **not** aggregate Chronus fragments. Inspect the tooling paths in [troubleshooting](troubleshooting.md) before invoking the wrapper; do not consent automatically to installation prompts.

```powershell
azpysdk changelog status sdk\evaluation\azure-ai-evaluation
# After authorization for local changelog/fragment edits:
azpysdk changelog create sdk\evaluation\azure-ai-evaluation
```

The wrapper calls `chronus changelog --package`. Check current CLI behavior and the complete diff: include notes exactly once, preserve categories/history and verify fragment consumption. Do not delete shared fragments still needed by other packages. The repository recommends Chronus; blocked manual collection needs maintainer-approved recovery, not a silent bypass.

## Prepare only after approval

Ask for the intended calendar date; do not infer it from local/UTC clocks. Replace the placeholder below with `MM/dd/yyyy`; the heading must be `## <version> (YYYY-MM-DD)`.

**Side effect:** after the version prompt, the script immediately creates/updates DevOps release tracking, before local edits. It can prompt for authentication and install Python tooling. Obtain authorization including the remote write; let the user answer prompts. Never replace a published heading.

```powershell
.\eng\common\scripts\Prepare-Release.ps1 -PackageName azure-ai-evaluation -ServiceDirectory evaluation -ReleaseDate '<MM/DD/YYYY>'
```

Independently inspect output, tracking, `_version.py` and changelog; exit zero is insufficient. Add the release section without renaming published history.

```powershell
.\eng\common\scripts\Verify-ChangeLog.ps1 -ChangeLogLocation .\sdk\evaluation\azure-ai-evaluation\CHANGELOG.md -VersionString '<version>' -ForRelease:$true
git diff --check
git --no-pager diff -- sdk\evaluation\azure-ai-evaluation .chronus\changes
```

Use the actual chosen version. A notes/version-only preparation does not justify rerunning costly live evaluations. Retain required CI evidence; functional changes need their relevant tests. Do not disable checks to obtain green results. See the [worked example](worked-example.md) for one release's concrete preparation-PR scope and dates.
