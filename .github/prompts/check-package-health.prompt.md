---
mode: "agent"
description: "Report the Azure SDK for Python health status of a package."
---

# Check package health

Use the available Azure SDK Python package-health tool to retrieve the package
health report.

- Include the report's **Last Refresh** date.
- Interpret statuses according to
  [`doc/repo_health_status.md`](../../doc/repo_health_status.md).
- Treat MyPy, Pylint, Sphinx, and Tests - CI as release-blocking checks. State
  clearly when any of them is not passing and the package is blocked.
- Link reported statuses when the health report provides links.
- Do not expose internal ownership fields such as `SDK Owned`.
- Separate passing checks, areas needing attention, and release blockers.
