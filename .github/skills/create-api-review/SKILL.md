---
name: create-api-review
license: MIT
metadata:
  version: "1.0.0"
  distribution: shared
description: 'Create an API review PR for an Azure SDK package using API Review Hub. **UTILITY SKILL**. USE FOR: "create API review", "open API review", "compare package versions", "APIView PR". DO NOT USE FOR: fixing APIView comments, SDK code generation, pipeline debugging. INVOKES: azure-sdk-mcp:azsdk_apireviewhub_request_review_pr.'
compatibility: "azure-sdk-mcp server v0.6.32 or later"
---

# Create API Review

This skill creates an API review pull request through API Review Hub for a package API surface comparison.

## Triggers

USE FOR: create API review, open API review, compare package versions, APIView PR
WHEN: "create API review", "open API review", "compare package versions", "APIView PR"
DO NOT USE FOR: fixing APIView comments, SDK code generation, pipeline debugging

## Rules

- Requires `azure-sdk-mcp` version `0.6.32` or later.
- Use `azure-sdk-mcp:azsdk_apireviewhub_request_review_pr` to create the review PR.
- CLI equivalent is `azsdk api-review create`.
- Language is fixed to `python` for this repository.
- Required user inputs: `packageName`, `targetBranch`.
- `baseTag` defines the baseline version. Use package tag format: `<packageName>_<version>`.
- If `baseTag` is omitted, ask the user to choose one of:
  - Use the latest GA (non-beta) release tag for `packageName`.
  - Provide a specific tag or version to use as baseline.
- `targetOwner` defaults to `Azure` when omitted.
- `targetRepo` is optional. When omitted, API Review Hub resolves repo by language.
- `targetOwner`, `targetRepo`, and `targetBranch` define where the review PR branch is created.
- Wait behavior mapping: `--no-wait` corresponds to `waitForCompletion: false`.
- Poll behavior mapping: `--poll-interval-seconds` corresponds to `pollIntervalSeconds` (default `30`).
- Optionally provide a ready-to-run `azsdk api-review create` command for the user with resolved values.

## MCP Tools

| Tool                                                  | Purpose                         |
| ----------------------------------------------------- | ------------------------------- |
| `azure-sdk-mcp:azsdk_apireviewhub_request_review_pr` | Create API review PR request    |
| `azure-sdk-mcp:azsdk_upgrade`                        | Check/upgrade MCP server version |

## Steps

1. **Collect Inputs** - Get required `packageName` and `targetBranch`. Optionally collect `baseTag`, `targetOwner`, and `targetRepo`.
2. **Prompt For Baseline** - If `baseTag` is not provided, ask the user to choose latest GA (non-beta) or provide a specific tag/version.
3. **Resolve Baseline** - If the user chooses latest GA, resolve and use the latest GA (non-beta) release tag for `packageName`. If the user provides a tag/version, use that value.
4. **Validate MCP Version** - Ensure `azure-sdk-mcp` is `0.6.32+`.
5. **Set Wait Mode** - Default to wait for completion. Use `waitForCompletion: false` only when user asks for no-wait behavior.
6. **Set Poll Interval** - If waiting for completion, use `pollIntervalSeconds` (default `30`, override only if requested).
7. **Request Review PR** - Run `azure-sdk-mcp:azsdk_apireviewhub_request_review_pr` with `language: python` and collected inputs.
8. **Return Result** - Provide review PR URL and operation status.
9. **Optional CLI Output** - If useful or requested, provide the equivalent `azsdk api-review create` command with all resolved arguments.

## CLI Command Template

```powershell
azsdk api-review create `
  --language python `
  --package-name <packageName> `
  --base-tag <baseTag> `
  --target-branch <targetBranch> `
  --target-owner <targetOwner> `
  --target-repo <targetRepo>
```

Optional flags:

- `--no-wait`
- `--poll-interval-seconds 30`
- `--output plain|json`

## Example

For `azure-storage-blobs` comparing `1.0.0` to the latest on main:

- `packageName`: `azure-storage-blobs`
- `baseTag`: `azure-storage-blobs_1.0.0`
- `targetOwner`: `Azure`
- `targetRepo`: `azure-sdk-for-python`
- `targetBranch`: `main`

## Troubleshooting

- If tool is missing or unsupported, run `azure-sdk-mcp:azsdk_upgrade` with `checkOnly: true` to verify current version.
- If `baseTag` is invalid, confirm the exact release tag name in the repository.
- If `baseTag` is omitted, confirm the user's baseline choice before requesting the review PR.
- If the generated review does not reflect expected changes, confirm `targetBranch` contains the intended newer API surface.
