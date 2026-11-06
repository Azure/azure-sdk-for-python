# Review, approval, and pipeline handoff

## Preparation PR

After authorization, commit the scoped diff and push to the approved fork/branch; never force-push. Use the app's `create_pull_request` in the correct session for a **draft** PR. No `gh pr create` authentication workaround. Verify the returned PR's base/head.

Copyable description:

```markdown
## Release
Prepare azure-ai-evaluation <version> for <YYYY-MM-DD> from main.

## Changes
- <Accurate changes since the published baseline; include breaking changes.>
- <Chronus aggregation and version classification rationale.>

## Evidence
- Published baseline and source SHA: <version; SHA>
- Changelog/version validation: <observed results>
- CI and API revision: <links; status or pending>
- Release tracking: <observed result>

## Approval
<Current API/release approvers and decisions, or unresolved blockers.>
No publication or compatibility exception is implied by this PR.
```

## Distinct approvals

Team convention: request access through [AzureSDK Partners](https://coreidentity.microsoft.com/manage/entitlement/entitlement/azuresdkpart-heqj) and request Python API review in [Language - Python - Reviews](https://teams.microsoft.com/l/channel/19%3A4175567f1e154a80ab5b88cbd22ea92f%40thread.skype/Language%20-%20Python%20-%20Reviews?groupId=3e17dcb0-4257-4a30-b843-77f47f1d4121). Verify current owners and Minsoo's release-approval role; obtain explicit approval for this release, not a prior one.

Use `azsdk_apiview_get_review_url` with `language: "Python"`, `package: "azure-ai-evaluation"`, `version: "<version>"`. Match revision to artifacts. Name approval is not revision/release approval. Inspect the actual gate: `azsdk_package_get_approval_status` can report **API Review Hub** (primary) and **APIView** (legacy) separately with different outcomes for the same package/version; a `reviewHub` result of `unknownPackage` is not a denial, and a final `isApproved: true` sourced from the legacy path still counts. Record which source approved.

For initial API evidence collection, have an authorized owner follow the current nonpublishing build procedure. Never promise a "Build > Analyze > Create API Review" task path or trigger publication to obtain review.

### Skip a new request when there is no public API diff

Before asking for a fresh review, compare the current main `api.md`/published baseline against the target release artifact or APIView revision for the package/version. If there is **no public API difference** and `azsdk_package_get_approval_status` already reports an approved revision for that package/version, document "no API changes" in the preparation PR/evidence and do **not** post a new API-review request — repeating an identical request wastes reviewer time. This is never a bypass: if the hash/revision differs from the approved one, the package is unrecognized by every source, or any gate explicitly fails, stop and obtain approval through the normal route. Code-review PR approval is still not release approval. See the [worked example](worked-example.md) for a release that used this path.

For read-only readiness, load the shared release skill and explicitly pass:

```json
{"packageName":"azure-ai-evaluation","language":"Python","branch":"main","checkReady":true}
```

to `azsdk_release_sdk`. Omitting `checkReady` **triggers release**. Readiness neither waives compatibility nor grants approval. Do not call publishing mode for the user.

## Choose the correct release route

Use [python-evaluation](https://dev.azure.com/azure-sdk/internal/_build?definitionId=7162), verifying the current definition, branch/source SHA and artifact version, not its display name or date.

Before an owner queues/reruns, compare the selected commit with the reviewed SHA. If main advanced, stop and review added changes rather than releasing its new head. Reconfirm the queued source/version. Internal links require organizational access; a sign-in page does not verify the target resource.

**Post-merge auto-release:** internal `IndividualCI` on main uses `AutoReleasePrepare`: merged PR, `auto-release` label, changed evaluation package and matching artifact. Coordinate approvals **before** labeled merge. The label enables release; applying it requires authorization and label permission, not merely PR authorship. The agent does not merge. Its documented `environment: none` caveat applies only to **this** route.

**Manual internal run:** templates support `Manual` without the label gate; declared artifacts remain eligible subject to other gates. Not an automatic skipped-CI fallback: an authorized owner follows the documented procedure, inspecting artifacts and human approval. Never invent queue parameters or use CLI publication when MCP is unavailable. A real evaluation release used this route without any `auto-release` label — confirm which route an owner actually used rather than assuming the label route by default; see the [worked example](worked-example.md).

Observe `Release_azureaievaluation`: skipped is not awaiting approval or published. [Diagnose](troubleshooting.md) before reruns; [verify publication](completion.md) before declaring success.
