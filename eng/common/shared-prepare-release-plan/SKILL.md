---
name: shared-prepare-release-plan
license: MIT
metadata:
  version: "1.0.0"
description: >-
  **UTILITY SKILL**
  Create and manage release plan work items for Azure SDK releases across languages.
  USE FOR: "create release plan", "update release plan", "link SDK PR to plan", "namespace approval", "check release plan status".
  DO NOT USE FOR: SDK generation, TypeSpec authoring, package validation, releasing packages (use shared-sdk-release).
  FOR SINGLE OPERATIONS: Use azsdk_get_release_plan directly to check plan status.
compatibility: >-
  Requires: azure-sdk-mcp server, API spec pull request in Azure/azure-rest-api-specs.
  Optional: Azure DevOps access for release plan work items.
---

# Prepare Release Plan

> Do not display Azure DevOps work item URLs. Only provide Release Plan Link and ID.

## Tools

| Tool                                          | Purpose              |
| --------------------------------------------- | -------------------- |
| `azsdk_create_release_plan`                   | Create release plan  |
| `azsdk_get_release_plan`                      | Get plan details     |
| `azsdk_get_release_plan_for_spec_pr`          | Find plan by PR      |
| `azsdk_update_sdk_details_in_release_plan`    | Update SDK info      |
| `azsdk_link_sdk_pull_request_to_release_plan` | Link SDK PR          |
| `azsdk_link_namespace_approval_issue`         | Link namespace issue |

## Steps

1. **Prerequisites** — Check for API spec PR; prompt if unavailable.
2. **Check Existing** — Query by plan number or spec PR link.
3. **Gather Info** — Collect Service Tree IDs, timeline, API version, release type. See `references/release-plan-details.md`.
4. **Create** — Run `azsdk_create_release_plan`.
5. **SDK Details** — Map emitters to languages. See `references/release-plan-details.md`.
6. **Namespace** — For mgmt plane first releases, link approval issue.
7. **Link PRs** — Link SDK PRs to plan.

## Related Skills

- `shared-sdk-release` — Trigger release pipeline
