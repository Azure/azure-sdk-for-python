# Local static check guide

Run from the target repository root. Discover commands there, not from a different language repository. Read the CI configuration and its templates to preserve flags, versions, dictionaries, exclusions, and link guidance.

## Changed files

Determine the actual PR target ref, verify it with `git rev-parse --verify`, and obtain the merge base with `git merge-base HEAD <target-ref>`. Use `git diff --name-only --diff-filter=d -z <merge-base>` for committed, staged, and unstaged changes together, plus `git ls-files --others --exclude-standard -z` for untracked files. Decode NUL-delimited paths without splitting spaces. Deduplicate and keep only existing files. List deletions separately when assessing project-level checks. Changes to shared lint configuration may require checking all projects that consume it.

An empty list is a no-op only after Git commands succeeded. A missing target ref or merge base must not silently produce a passing result.

## Spelling

Where CI uses `eng/common/spelling/Invoke-Cspell.ps1`, reuse it with an explicit file list (including uncommitted files):

```powershell
# $files contains the absolute changed-file paths; $config is CI's cspell config.
$errors = & ./eng/common/spelling/Invoke-Cspell.ps1 `
    -FileList $files -CSpellConfigPath $config -SpellCheckRoot (Get-Location).Path
$code = $LASTEXITCODE
$errors
if ($code -ne 0 -or $errors) { throw "Spelling check failed." }
```

Run this in a separate `pwsh` process and check its exit code. Do not invoke the spelling helper without a real config: not every repository enables cspell. For committed changes only, CI's `check-spelling-in-changed-files.ps1` requires explicit `-SourceCommittish HEAD`, `-TargetCommittish <target-ref>`, and `-ExitWithError`; its pipeline-environment defaults can otherwise check nothing locally.

## Links

For changed Markdown/HTML covered by CI's link check, reuse `eng/common/scripts/Verify-Links.ps1`. For example, in PowerShell:

```powershell
# $docs contains the absolute changed-document paths.
& ./eng/common/scripts/Verify-Links.ps1 -urls $docs -recursive:$false `
    -rootUrl ([System.Uri]::new((Get-Location).Path + "/").AbsoluteUri)
```

Use a separate `pwsh` process because this script exits. Supply the target workflow's additional flags, such as `-ignoreLinksFile`, `-checkLinkGuidance`, `-allowRelativeLinksFile`, local repository mapping, and cache settings. Do not call with an empty document list. Report unreachable links or unavailable network access as blocked validation, not success; preserve diagnostics for user review.

## Project checks

Inspect the affected project's CI and README before selecting a command. Use locked dependencies and non-mutating check modes where available:

| Area                  | Existing checks to look for                                    |
| --------------------- | -------------------------------------------------------------- |
| JavaScript/TypeScript | Manifest scripts for lint, format check, and type checking     |
| Python                | CI's lint/type-check commands and configured environment       |
| .NET                  | CI's formatting/analyzer checks; analyzers may require a build |
| PowerShell            | Configured script analysis checks                              |
| Skills                | Existing Prettier checks and Vally skill/eval lint             |

For Azure SDK Tools skills, install existing dependencies with `npm ci --prefix .github` and `npm ci --prefix eng/skill-eval`. Run `.github/node_modules/.bin/prettier --check <changed-skill-files>` and `eng/skill-eval/node_modules/.bin/vally lint <changed-skill-directory> --strict`. Use project-wide checks when changed-file scoping is unsupported. Run applicable evals and tests separately; static checks are not a replacement.

For SDK packages, use the repository's existing package check commands or `azsdk_package_run_check` when available, but also run repository-level checks for changed docs and non-SDK code. Do not assume that a package checker covers every changed path.
