# Evaluation release artifacts

This is a release-workflow specialization, not a generated-code customization inventory. Do not regenerate the SDK or change CI to prepare a release.

Paths below are repository-relative unless marked package-relative. Re-read current sources when behavior differs from this guide.

| Owned artifact | Release responsibility |
|---|---|
| `sdk\evaluation\azure-ai-evaluation\azure\ai\evaluation\_version.py` | `VERSION` is the package source version; compare it with the target changelog heading and built package metadata. |
| `sdk\evaluation\azure-ai-evaluation\CHANGELOG.md` | Canonical release notes. Preserve already-published sections; a dated heading alone does not prove publication. |
| `.chronus\changes\` | Pending changes may be absent from the changelog. Select evaluation entries, including shared multi-package fragments. |
| `sdk\evaluation\azure-ai-evaluation\README.md`; package-relative `samples\`, `api.md` | Review user-facing changes against the published API; local API snapshots alone are not the published baseline. |
| `sdk\evaluation\azure-ai-evaluation\pyproject.toml` | Check actual validation configuration. Disabled checks are not PASS results or permission to waive release gates. |
| `sdk\evaluation\ci.yml` | `ServiceDirectory: evaluation`, artifact `azure-ai-evaluation`, `safeName: azureaievaluation`. Do not substitute a different service pipeline. |

## Sources of behavior

| Repository source | Consult for |
|---|---|
| `eng\common\scripts\Prepare-Release.ps1` | Version prompt, release date, tracking-before-local-edits ordering. |
| `eng\common\scripts\Helpers\DevOps-WorkItem-Helpers.ps1` | `Update-DevOpsReleaseWorkItem` creates or updates release tracking. |
| `eng\scripts\Language-Settings.ps1` | Python version setter, tool installation, PyPI version enumeration. |
| `eng\common\scripts\Verify-ChangeLog.ps1` | Supported validation parameters. |
| `.chronus\config.yaml`, `.github\chronus\package.json` | Change kinds, package discovery, pinned tooling. |
| `eng\tools\azure-sdk-tools\azpysdk\changelog.py` | Package-scoped status/create commands and installation-path assumptions. |
| `eng\pipelines\templates\stages\archetype-python-release.yml`, `release-artifact.yml` in the same directory | Manual versus post-merge gates, release jobs, next-version PR. |
| `eng\common\scripts\Resolve-AutoReleasePackages.ps1`, `AutoRelease-Operations.ps1` in the same directory | Source-commit PR resolution, required label, changed-package intersection, fail-closed outputs. |

Authoritative guidance: [Python design guidelines](https://azure.github.io/azure-sdk/python_design.html), repository `doc\dev\release.md`, `doc\dev\package_version\package_version_rule.md`, and `doc\dev\changelog_updates.md`. Use shared `.github\skills\azsdk-common-sdk-release\SKILL.md` for MCP release tooling and `.github\skills\azsdk-common-pipeline-analysis\SKILL.md` before pipeline analysis.

## Team conventions, not repository-wide rules

The evaluation team's supplied process normally releases from main. Confirm current owners and applicability: optional freeze plus two-day ASK MODE requiring manager approval; merging the release-preparation PR begins the official freeze. Fixes still require reviewed PRs and applicable ASK MODE approval.

Confirm whether Minsoo remains the explicit evaluation release approver. Previous-release approval, package-name approval, API-revision approval, and publication-stage approval are different evidence; none substitutes for the others.
