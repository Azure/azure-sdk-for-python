# On-demand sample tests in Azure DevOps

[../../../tests.yml](../../../tests.yml) runs existing synchronous/asynchronous pytest sample cases in up to **four fresh public-network Standard Foundry environments**, sharing one permanent set of managed identities. Each test queue creates its own resource group (RG) and deletes only its owned temporary resources.

## Workflow

| `runMode` | Behavior |
| --- | --- |
| `preview` (default) | Collect samples without execution and publish a separate fresh plan for each queue. No Azure resources are queried or changed. |
| `run-and-cleanup` | Generate plans, check shared identities and aggregate capacity, then provision/test/clean up each nonempty queue in parallel. |

Preview is **plan-only**, not ARM `what-if`, a permission/capacity check, or a regression-test job. Pester installation and unit-test execution are not part of an on-demand sample run. Maintainer checks are described below.

Defaults: **up to four RG workers**, **West US 3** (`westus3`), **gpt-5.2**, version **2025-12-11**, `GlobalStandard`, capacity **10 per active queue**. `testQueueCount` accepts 1–4 as a maximum; fewer samples produce fewer workers, never empty RGs. Model settings remain configurable and `modelVersion=auto` resolves the regional catalog default. The reviewed shared-identity composition currently supports only West US 3.

Selected cases are sorted by pytest node ID and divided **round-robin, without repetition**. Five cases across four workers assign cases 1 and 5 to `q1`, case 2 to `q2`, case 3 to `q3` and case 4 to `q4`. Each worker runs its assigned cases sequentially, independently of the other workers.

The default selection is [the synchronous MCP project-connection sample](../../../samples/agents/tools/sample_agent_mcp_with_project_connection.py) and [its asynchronous counterpart](../../../samples/agents/tools/sample_agent_mcp_with_project_connection_async.py): **two total cases in two RGs**, each executed once. These are execution queues, not Azure Storage queue resources.

## One-time setup

Configure a pipeline to use [../../../tests.yml](../../../tests.yml), authorize the Azure SDK package feed and `azsdk-pool`, and save these variables:

| Variable | Setting |
| --- | --- |
| `AZURE_SUBSCRIPTION_ID` | Normal variable containing the target subscription GUID. |
| `AZURE_TENANT_ID` | Normal variable containing the target tenant GUID. |
| `LLM_VALIDATION_PROJECT_ENDPOINT` | Existing Foundry project endpoint. A normal variable is supported; secret storage is optional. |
| `MCP_GITHUB_PAT` | **Secret** containing the complete GitHub PAT, including `github_pat_` or `ghp_`. Required for the MCP sample. |

The target IDs must be available to **both** Preview and RunSamples. Runtime values may also come from the authorized group selected by `secretVariableGroup`, but that group is scoped only to RunSamples. Do not put secrets in YAML, chat, runtime parameters, command-line arguments, plans or artifacts.

Set `azureServiceConnection` to an authorized **Azure Resource Manager connection name**, preferably using workload identity federation. Its service principal must already have:

- Access to the explicit subscription and tenant; resource-group/deployment permissions, attachment of the existing UAMIs, and native Cosmos SQL role-assignment permissions. **Contributor** covers these management operations; workers do not need Azure IAM-administrator roles.
- The preconfigured subscription-scoped **Foundry User** grant checked by admission. Workers only verify Azure IAM grants; they never create or repair them.
- Access to the existing validation project and its **gpt-5.2** deployment, including the harness's file-upload and Code Interpreter operations. No validator resources or roles are provisioned by this pipeline.
- Registered providers: `Microsoft.CognitiveServices`, `Microsoft.Storage`, `Microsoft.DocumentDB`, `Microsoft.Search`, and `Microsoft.ManagedIdentity`.

The scripts require **PowerShell 7.2+**. Azure subscription roles do not grant Azure DevOps pipeline-edit or service-connection authorization rights. Existing organization/service-connection approvals are not bypassed.

Enter the PAT directly in the pipeline secret field or an authorized Library secret. Use minimum GitHub permissions and an appropriate expiration/SSO authorization; see [GitHub MCP authentication](https://github.com/github/github-mcp-server/blob/main/docs/remote-server.md).

### Permanent identities and service grants

An authorized administrator separately runs [validation/Initialize-SharedSampleIdentities.ps1](validation/Initialize-SharedSampleIdentities.ps1). Supply the target IDs through the two environment variables above and explicit pipeline/caller identifiers through its mandatory parameters. First run the default dry run, review it and obtain explicit approval, then use `-Apply` with the same saved preview. Finish with `-VerifyOnly`. Keep the local state: applied or ambiguous attempts must be reconciled, never replayed or automatically deleted.

[infra/bootstrap-identities.bicep](infra/bootstrap-identities.bicep) creates only:

- Permanent RG `rg-azsdk-sample-identities-wus3` and four UAMIs named `mi-azsdk-sample-{project,account,search,function}-wus3`.
- Six **subscription-scoped** roles for the project UAMI: Foundry User, Storage Blob Data Contributor, Storage Blob Data Owner, Cosmos DB Operator, Search Service Contributor and Search Index Data Contributor.
- Subscription-scoped Foundry User for the established pipeline principal. Existing Contributor access is unchanged; no Owner, User Access Administrator or RBAC Administrator is granted.

The other three identities have **no grants** until a separately reviewed integration needs them. Bootstrap creates no test workloads. The CI cleanup never deletes these identities or grants.

**Scope warning:** the service grants reach matching existing and future resources throughout the subscription, not just temporary RGs. Shared identities reduce cross-run isolation. The approved Blob Owner condition restricts only blob tag read/write and filtering to container names ending `-azureml-agent`; it omits the original generated workspace-prefix restriction, and other Blob Owner permissions remain allowed. Do not silently broaden this pattern or use it without scope review.

### Single-operator execution; no Environment setup

No dedicated ADO Environment, Exclusive lock, ADO access-token mapping or Environment-administration permission is needed by this workflow. All jobs are ordinary pipeline jobs. Existing checks on service connections, pools and other protected resources remain in force.

**The sole operator must verify that the previous run and every RG cleanup have completed before starting another live run.** The four-worker limit applies per run, not across runs; an accidental overlapping run is not automatically serialized and can exceed four RGs overall.

Read-only admission still rejects leftover temporary sample RGs, repeated/empty queue selections and insufficient aggregate account/Search/model quota. This is a point-in-time check, not a race-free mutex or hardware reservation. The default two cases need two free account and Search slots and 20 model units; four active workers need four slots and 40 units. This workflow limit is not an Azure security boundary.

## Run a sample

1. Select the reviewed branch in **Run pipeline**.
2. Start with `runMode=preview`, `selectionKind=sample-path`, and the default `selection`.
3. Inspect the full selection, the per-queue selections/plans under `q1` through the active queue count, and the worker matrix in the **sample-plan** artifact. Confirm every selected node appears exactly once across queue plans.
4. Once the variables, service connection and permissions are configured, queue `runMode=run-and-cleanup` with the same selection. This opts in to billable resources and cleanup after the plan succeeds; there is no YAML manual-approval stage.
5. Verify every queue's ADO **Tests** results and attachments and final deployment state `CleanedUp` in **sample-results-q1** through **sample-results-q4**, as applicable.

To verify repeatability, wait for all queues to pass and finish verified cleanup before queueing a second fresh batch. Each queue gets a new plan, owner token and RG; shared identities alone persist. Never reuse the first batch's workloads or overlap retries.

### Selection examples

| `selectionKind` | `selection` |
| --- | --- |
| `sample-path` | `samples/agents/tools/sample_agent_mcp_with_project_connection.py` |
| `sample-path` | `samples/agents/tools/sample_agent_mcp*project_connection*.py` (sync and async) |
| `test-id` | `sample_agent_mcp_with_project_connection` |
| `test-id` | `*test_samples_async.py::*[sample_agent_mcp_with_project_connection_async]` |
| `test-id` | `sample_agent_basic;sample_agent_mcp_with_project_connection` (OR) |

`*` and `?` are wildcards; brackets in pytest IDs are literal. Matching is case-insensitive, slash-normalized and deduplicated. Semicolons/newlines separate OR patterns. Zero matches fail; selection never falls back to all tests. Harness exclusions remain excluded. Unsupported required sample inputs fail during planning instead of inventing resources or values.

## Safety and results

- **Explicit targets and identity:** task, plan and state subscription/tenant IDs must match the same authorized service-principal identity. No fallback to an active account, another tenant, or a developer's login.
- **Live preflight:** check provider registration, Search S1 offerings/service quota, Cosmos subscription-region access, the pinned template's Storage SKU restrictions, model availability, and separate account/model quotas. Missing or invalid evidence fails closed. These checks do not reserve capacity or change region, SKU, registration or policy.
- **Reviewed local Bicep:** [infra/standard-shared-identities.bicep](infra/standard-shared-identities.bicep) is a local UAMI composition based on the unchanged official reference pinned by [infra/standard-setup.lock.json](infra/standard-setup.lock.json), not an unchanged upstream deployment. The official 14 sources remain checksum-verified maintainer references; workers do not download them. State is saved before the first resource mutation.
- **Fresh workloads only:** every queue creates a Foundry account/project, Storage, Cosmos DB, Search, three AAD connections, two capability hosts, a native Cosmos data grant, one model deployment and an MCP connection. Only the four pinned UAMIs are reused. No worker Azure IAM assignments, Application Insights, Function App or ACR are created. `GlobalStandard` inference may run globally despite resource colocation.
- **Secrets:** only provisioning receives the PAT, through an environment-backed Bicep `@secure()` parameter. The connection stores the full Bearer token; the sample receives only its connection ID. No job explicitly maps an ADO access token; the sample subprocess strips any inherited token and the PAT. The external validator endpoint is passed only through the preflight/test environment and excluded from plans, state, Bicep outputs and pytest arguments.
- **Readiness:** bounded read-only retries precede sample execution. An already-started sample is never retried automatically.
- **Logs:** results attach the shared executor's sanitized API/print log and print-only output log through native JUnit markers. Captured console/JUnit reports are redacted; raw sample prints/live logging cannot bypass capture. Only verified run-owned attachment paths are published. Validator input remains the original in-memory output. Logs can still contain test data; use suitable access and retention settings.
- **Cleanup:** each queue's `always()` step attempts deletion after failure/cancellation, verifying its independently supplied queue, exact state/plan binding, full group ID and all four CI purpose/run/owner/queue tags. The group must be absent before recording `CleanedUp`; `-WhatIf` never marks completion. Sibling queues, shared identities/validation resources, permanent grants and separately retained projects are untouched.

Provisioning can incur standing charges. Agent loss, hard termination or Azure errors can prevent cleanup; expiry tags are metadata, **not automatic deletion**. Review state and inventory before manual cleanup. Soft-deleted Foundry records are not purged automatically. Use task errors, per-queue state/inventory and pytest output for troubleshooting; raw secure deployment bodies are suppressed. Compilation and bootstrap verification do not prove live UAMI Standard deployment or sample success.

## Files

| Runtime file | Responsibility |
| --- | --- |
| [New-SampleDeploymentPlan.ps1](New-SampleDeploymentPlan.ps1) | Fresh queue-bound plan, explicit targets and required-input checks. |
| [Invoke-SampleProvisioning.ps1](Invoke-SampleProvisioning.ps1) | Read-only batch admission, local Bicep deployment, state and inventory. |
| [Remove-SampleResources.ps1](Remove-SampleResources.ps1) | Exact queue/ownership-checked cleanup. |
| [SampleCiHelpers.ps1](SampleCiHelpers.ps1) | Shared identity/grant, nonempty/disjoint selection, quota and error-handling guards. |
| [select_samples.py](select_samples.py), [run_samples.py](run_samples.py) | Real sample collection/selection and live pytest invocation. |
| [sample_ci_attachments.py](sample_ci_attachments.py) | Sanitized shared-log attachments and captured report publication. |

## Maintainer validation (separate from sample runs)

Retained Python unit tests live in this directory; mocked PowerShell tests and [the Bicep checker](validation/Test-BicepTemplates.ps1) live under [validation](validation). No new PR pipeline is introduced here.

- With dotenv/live execution disabled, run the Python tests using `--confcutdir=tests/samples/ci` to avoid parent service fixtures.
- Run the PowerShell `*.Tests.ps1` files under validation using the existing compatible **Pester 4.10.1** environment. They mock Azure calls and do not provision resources. On-demand pipeline agents do not need Pester.
- The Bicep checker always compiles five local templates and fictional sample parameters with an empty PAT. Its optional `StandardTemplatePath` input also verifies and compiles the 14 unchanged cached official sources. It rejects worker Azure IAM writes while allowing the separate administrator bootstrap's approved grants.
- Use the repository Black configuration, PowerShell syntax checks and `git diff --check`. Real harness collection must use `PYTHON_DOTENV_DISABLED=true` and fictional target IDs and must not execute samples.
