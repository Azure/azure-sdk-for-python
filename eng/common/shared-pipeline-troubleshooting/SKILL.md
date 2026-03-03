---
name: shared-pipeline-troubleshooting
license: MIT
metadata:
  version: "1.0.0"
description: >-
  **UTILITY SKILL**
  Diagnose and resolve failures in Azure SDK CI pipelines and SDK generation pipelines.
  USE FOR: "pipeline failed", "build failure", "CI check failing", "SDK generation error", "reproduce pipeline locally", "debug SDK pipeline".
  DO NOT USE FOR: TypeSpec authoring, release plans, APIView feedback (use shared-apiview-feedback-resolution), package publishing.
  INVOKES: azsdk_analyze_pipeline, azsdk_verify_setup, azsdk_package_build_code, azsdk_package_run_check.
  FOR SINGLE OPERATIONS: Use azsdk_analyze_pipeline directly for quick failure analysis.
compatibility: >-
  Requires: azure-sdk-mcp server, Azure DevOps pipeline build ID.
  Optional: local clone of SDK repo for reproducing failures.
---

# PR and CI Pipeline Troubleshooting

## Prerequisites

Requires `azure-sdk-mcp` MCP server for pipeline analysis and local reproduction tools.

## MCP Tools

| Tool                       | Purpose                   |
| -------------------------- | ------------------------- |
| `azsdk_analyze_pipeline`   | Analyze pipeline failures |
| `azsdk_verify_setup`       | Verify local environment  |
| `azsdk_package_build_code` | Reproduce build locally   |
| `azsdk_package_run_check`  | Run validation checks     |

## Steps

1. **Identify Failure** — Get build ID, run `azsdk_analyze_pipeline`. Categorize failure type.
2. **Analyze Root Cause** — See `references/failure-patterns.md` for common patterns.
3. **Reproduce Locally** — Run `azsdk_verify_setup`, then `azsdk_package_build_code` or `azsdk_package_run_check`.
4. **Apply Fixes** — Use direct edits for code fixes or TypeSpec changes.
5. **Verify** — Confirm fix locally, push changes, monitor pipeline re-run.

## CLI Fallback

Without MCP: view pipeline logs directly in Azure DevOps browser UI at the build URL, download logs, and inspect failure stages manually.
