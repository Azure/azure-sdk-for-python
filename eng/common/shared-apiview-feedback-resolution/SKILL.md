---
name: shared-apiview-feedback-resolution
license: MIT
metadata:
  version: "1.0.0"
description: >-
  **UTILITY SKILL**
  Retrieve and resolve feedback from APIView reviews on Azure SDK packages.
  USE FOR: "APIView comments", "resolve API review feedback", "rename type per reviewer", "SDK API surface changes", "regenerate SDK after review".
  DO NOT USE FOR: creating TypeSpec projects, SDK generation from scratch, release plan management, package publishing.
  INVOKES: azsdk_apiview_get_comments, azsdk_typespec_delegate_apiview_feedback, azsdk_run_typespec_validation, azsdk_package_generate_code.
  FOR SINGLE OPERATIONS: Use azsdk_apiview_get_comments directly to fetch comments.
compatibility: >-
  Requires: azure-sdk-mcp server, SDK pull request with APIView review link.
  Optional: TypeSpec project for TypeSpec-based customizations.
---

# APIView Feedback Resolution

## MCP Tools Used

| MCP Tool                                   | Purpose                     |
| ------------------------------------------ | --------------------------- |
| `azsdk_apiview_get_comments`               | Retrieve APIView comments   |
| `azsdk_typespec_delegate_apiview_feedback` | AI-resolve APIView feedback |
| `azsdk_run_typespec_validation`            | Validate TypeSpec changes   |
| `azsdk_package_generate_code`              | Regenerate SDK              |

## Steps

1. **Retrieve Comments** — Get APIView revision URL from SDK PR, run `azsdk_apiview_get_comments`.
2. **Categorize** — Group as Critical/Suggestions/Informational. See `references/feedback-resolution-steps.md`.
3. **Resolve** — For TypeSpec changes, use `azsdk_typespec_delegate_apiview_feedback`. For code-only fixes, apply directly. See `references/feedback-resolution-steps.md`.
4. **Validate & Regenerate** — Run validation, regenerate SDK, build and test.
5. **Confirm** — Verify all items addressed, inform user to request re-review.

## MCP Prerequisites

Requires `azure-sdk-mcp` server connected and authenticated.

## CLI Fallback

Without MCP, review APIView comments in browser and apply fixes to TypeSpec or SDK code directly.
