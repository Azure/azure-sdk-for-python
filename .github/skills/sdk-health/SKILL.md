---
name: sdk-health
description: "Report Azure SDK for Python package health. USE FOR: package health status, release-blocking health checks, repository health report. DO NOT USE FOR: fixing checks, pipeline diagnosis, or triggering releases."
---

# Report Python SDK Health

Use the configured Azure SDK Python health-status tool to retrieve current
package health. If the tool is unavailable, say that current status could not
be retrieved; do not infer live status from static documentation.

Report:

- the package and report's `Last Refresh` date
- overall status
- passing checks
- checks needing attention
- release-blocking checks

MyPy, Pylint, Sphinx, and Tests - CI are release-blocking. If any are not
passing, state clearly that the package is blocked from release. Link reported
statuses to their supplied URLs when available. Do not expose internal
ownership fields such as `SDK Owned`.

Use [`../../../doc/repo_health_status.md`](../../../doc/repo_health_status.md)
to interpret statuses. Do not diagnose or fix failures unless the user asks;
route those requests to the pipeline analysis or fixer skill.

## Example

> As of <Last Refresh date>, here is the health status for azure-ai-projects:
>
> Overall Status: ⚠️ NEEDS_ACTION
>
> ✅ Passing: Pyright, Sphinx
>
> ⚠️ Needs attention: Pylint (WARNING), Tests - Samples (DISABLED),
> Customer-reported issues (5 open)
>
> ❌ Release blocking: MyPy (FAIL), Tests - CI (FAIL)
>
> This library is failing two release-blocking checks — MyPy and Tests - CI —
> so it is blocked from release.
