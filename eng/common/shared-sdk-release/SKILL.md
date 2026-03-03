---
name: shared-sdk-release
license: MIT
metadata:
  version: "1.0.0"
description: >-
  **UTILITY SKILL**
  Check SDK package release readiness and trigger the release pipeline for Azure SDK packages.
  USE FOR: "release SDK", "trigger release", "check release readiness", "release pipeline", "publish package", "ship SDK".
  DO NOT USE FOR: release plan creation (use shared-prepare-release-plan), SDK generation.
  INVOKES: azsdk_release_sdk.
  FOR SINGLE OPERATIONS: Use azsdk_release_sdk with checkReady=true for readiness check only.
compatibility: >-
  Requires: azure-sdk-mcp server, SDK package merged in azure-sdk-for-{language} repo on release branch.
  Supports: .NET, Java, JavaScript, Python, Go.
---

# SDK Release

## MCP Tools

| Tool                | Purpose                                                     |
| ------------------- | ----------------------------------------------------------- |
| `azsdk_release_sdk` | Check release readiness and/or trigger the release pipeline |

## Steps

1. **Collect Info** — Get `packageName` and `language` from the user. Optionally get the `branch` (defaults to main).
2. **Check Readiness** — Run `azsdk_release_sdk` with `checkReady: true` to verify:
   - API review approval status
   - Changelog completeness
   - Package name approval (for new preview packages)
   - Release date set in release tracker
3. **Review Results** — If not ready, display failing checks and guide the user to resolve issues.
4. **Trigger Release** — Once ready, run `azsdk_release_sdk` with `checkReady: false` to trigger the pipeline. Show the release pipeline link to the user and inform them they must approve the release stage after triggering.

## Prerequisites

Azure SDK MCP server must be running. No CLI fallback — if MCP is unavailable, prompt user to configure it.

## Related Skills

- `shared-prepare-release-plan` — Create release plan work item
