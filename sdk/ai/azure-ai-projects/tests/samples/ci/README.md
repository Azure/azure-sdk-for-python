# On-demand sample tests in Azure DevOps

[../../../tests.yml](../../../tests.yml) runs the existing synchronous and asynchronous pytest sample harness against a new, temporary **Standard Foundry project**. Provisioning uses **Bicep**, not imperative resource-creation scripts.

The first-run default is [../../../samples/agents/tools/sample_agent_mcp_with_project_connection.py](../../../samples/agents/tools/sample_agent_mcp_with_project_connection.py). The same selector can choose its async counterpart or other collected sample tests.

## What happens

1. Collect the real cases in [../test_samples.py](../test_samples.py) and [../test_samples_async.py](../test_samples_async.py). Do not execute samples during collection.
2. Match the sample-path or test-ID wildcard and show the exact selected cases. Zero matches fail; the pipeline never falls back to all tests.
3. Require `AZURE_SUBSCRIPTION_ID` and `AZURE_TENANT_ID` from pipeline environment variables and include both explicit targets in a non-secret provisioning plan, download integrity-pinned official Standard setup **Bicep sources**, and compile all templates. The default `preview` mode ends here and makes no Azure changes.
4. In `run-and-cleanup` mode, continue automatically after this run's fresh preview succeeds. There is no YAML manual-approval stage. Selecting this mode when queueing explicitly opts in to creating billable resources and deleting this run's temporary resources afterward.
5. Authenticate with the authorized Azure Resource Manager service connection and verify access to the plan's `AZURE_SUBSCRIPTION_ID` in `AZURE_TENANT_ID` using the same application. Never fall back to the connection's default subscription or tenant. Check provider registration, regional dependency eligibility, model availability, Cognitive Services `AccountCount` quota, and model-deployment quota before creating a resource group, then deploy Bicep to create:
   - A uniquely named, run-owned resource group.
   - A Foundry account and project with managed identities.
   - A Storage account, Cosmos DB account, AI Search service, project connections, capability hosts and runtime role assignments: the official **Standard agent setup**.
   - Only the selected sample model. Output validation reuses the already-deployed **gpt-5.2** model in the existing validation project; no validation model is provisioned.
   - A project-scoped GitHub MCP connection when the selected sample requires `MCP_PROJECT_CONNECTION_ID`.
6. Use the `LLM_VALIDATION_PROJECT_ENDPOINT` environment variable for output validation. Wait up to ten minutes for the temporary sample project's readiness, then run only the selected pytest node IDs with live mode on and recording off. Publish JUnit results to the ADO **Tests** tab.
7. Run cleanup even after failure or cancellation, verifying the resource-group ID and every ownership tag before deleting **only this run's temporary resource group**. Capture non-secret resource inventories before/after deployment.

PowerShell orchestrates Bicep and cleanup; Python collects and invokes the existing tests. Neither provisions Azure resources imperatively. Cleanup is necessarily a resource-group deletion rather than a Bicep deployment.

## One-time administrator setup

### Pipeline and Azure access

- Configure an on-demand pipeline to use the package's [../../../tests.yml](../../../tests.yml), then select the reviewed branch in **Run pipeline**. An existing pipeline needs no definition update if its YAML path is unchanged.
- Set the normal pipeline variables `AZURE_SUBSCRIPTION_ID` and `AZURE_TENANT_ID` to the intended subscription and tenant GUIDs. Neither value is hardcoded in the YAML or supplied as a Run pipeline parameter. Both must be available to Preview and RunSamples; a variable group scoped only to RunSamples is insufficient. The YAML explicitly maps both into each relevant task's environment. Missing, malformed or unresolved values fail closed. The preview records both targets, and provisioning, tests and cleanup verify them against the plan, deployment state and authenticated identity.
- An administrator must make an **Azure Resource Manager service connection** available to this pipeline; **workload identity federation** is recommended. Enter its name in `azureServiceConnection`.
- The connection must already have access to the requested subscription in the exact `AZURE_TENANT_ID`. Each Azure task selects that subscription only within its already-authenticated application identity. A different tenant, inaccessible subscription or changed target stops the run before resource changes; these variables do not grant access or change how the service connection authenticates. `azureServiceConnection` is the authorized ARM connection name, not the subscription GUID. Do not reuse a connection to an unrelated test tenant.
- Provisioning creates a new resource group, so the connection needs subscription-level resource-group/deployment permissions plus management and role-assignment permissions on the new resources. Use an administrator-approved role configuration, for example **Contributor + Role Based Access Control Administrator**, with reviewed scopes and assignment conditions. Merely having Foundry User is insufficient to provision Standard setup. Cleanup remains restricted to the run-owned group regardless of the connection's broader permissions.
- Register `Microsoft.CognitiveServices`, `Microsoft.Storage`, `Microsoft.DocumentDB`, and `Microsoft.Search` in advance. Preflight fails rather than registering providers automatically.
- Ensure the selected region supports Standard Foundry, Cosmos DB, Search, and the selected sample model with sufficient quota. Defaults: **West US 3** (`westus3`), **gpt-5.2**, version **2025-12-11**, `GlobalStandard`, capacity **10**. Use `modelVersion=auto` explicitly to resolve the regional catalog's default. The external validation project must already have deployment **gpt-5.2**. Regional offerings, quota and policy can change; preflight does not reserve capacity.
- The orchestration scripts require **PowerShell 7.2 or later**. Preview runs both pytest and the mocked PowerShell safety tests using pinned **Pester 4.10.1** before creating the deployment plan. The shared repository module helper uses the **Azure SDK tools feed**, not PSGallery. That exact Pester version must be preinstalled or available from the approved feed; a newer version is not substituted. Ask the agent/feed administrator if bootstrap fails before tests run.
- Authorize the pipeline's use of the Azure SDK package feed and the `azsdk-pool` agent pool. The pipeline reuses the repository's 1ES template and feed-authentication steps. The feed supplies the development-only resource detector dependency.

ADO permissions are independent: permission to **queue** a pipeline does not imply permission to **edit** it, preview modified YAML, save variables/secrets, create Library groups, or authorize a service connection. Ask a pipeline/Library administrator for the necessary setup; do not change identities or bypass those controls.

### Configure the existing validation project endpoint

An administrator opens **Pipelines → this pipeline → Edit → Variables → New variable**, names it `LLM_VALIDATION_PROJECT_ENDPOINT`, enters the existing project's endpoint, and saves. A **normal pipeline variable is supported**; the secret flag is optional for this endpoint, unlike the GitHub PAT. Alternatively, store it in the authorized group selected by `secretVariableGroup`. Do not commit the value, use a Run pipeline parameter, or pass it on a command line.

The pipeline maps the endpoint explicitly only to a configuration-preflight step and the live test task. The endpoint-shape check runs **before resource provisioning**, without echoing the value or calling Azure. A missing value or unresolved ADO variable fails closed. The runner passes it to pytest through the environment; the test configuration preserves it rather than replacing it with a preparer default.

The preflight verifies the subscription and tenant and authenticates through the same service connection as the test task, then saves only its application/client ID, principal/object ID and tenant ID in the **pipeline-identity** artifact under **sample-results**. It never saves a token or other authentication claims. This identifies the actual caller for a scoped RBAC investigation even if the validation endpoint is missing. It does not grant roles or prove access to the external project; role and tenant checks must use the project tenant's correct application principal.

The service-connection identity used by the test task must already have the access required for output validation on that project and its model (including the existing harness's file upload and Code Interpreter calls). A model being deployed does not by itself grant this identity access. The pipeline does not create or update the validation project/model, assign roles on it, or delete it during cleanup. The preflight is not an access or quota check on that shared project.

The endpoint is excluded from deployment plans, Bicep parameters/outputs, deployment state and pytest arguments, regardless of the variable's secret flag. Shared sample logging and JUnit failure capture redact it; validation status messages do not print it. Existing test-data and attachment-retention precautions still apply.

### Save the GitHub PAT as a secret

The MCP service is GitHub, so this is a **GitHub PAT**, not an Azure DevOps PAT.

Choose one supported storage location:

1. **Pipeline secret**: a pipeline administrator opens **Pipelines → this pipeline → Edit → Variables → New variable**, sets the name to `MCP_GITHUB_PAT`, enters the **complete token including its prefix** (`github_pat_…` or `ghp_…`), checks **Keep this value secret**, and saves. Leave `secretVariableGroup=none`.
2. **Library secret**: a Library administrator creates or updates an approved variable group, adds `MCP_GITHUB_PAT` with its **lock/secret setting enabled**, and authorizes only the intended pipeline. Set `secretVariableGroup` to that group's name.

Enter the value **directly in the ADO secret field**. Do not paste it into chat, YAML, runtime parameters, source control, artifacts, or logs. Do not assume pipeline-variable editing is available to a user who lacks pipeline edit permission.

Use the minimum GitHub token permissions needed by the MCP tools this sample calls, a short expiration, and any required organization/SSO authorization. The sample queries the authenticated GitHub profile; do not grant repository write permissions merely to run this test. Refer to [GitHub MCP authentication guidance](https://github.com/github/github-mcp-server/blob/main/docs/remote-server.md) for current token support and requirements.

Only the provisioning task receives `MCP_GITHUB_PAT`. [infra/sample-resources.bicepparam](infra/sample-resources.bicepparam) reads it from the process environment and supplies the Bicep `@secure()` parameter. The connection stores `Authorization = Bearer <complete-token>`, category `RemoteTool`, authentication `CustomKeys`, metadata `type=custom_MCP`, and `isSharedToAll=false`.

This matches the connection contract in the supplied project-pool reference, but **does not blindly prepend `github_pat_`**. Supplying a full token avoids a duplicate token prefix. The test process receives the **connection resource ID**, never the PAT. Deployment-state and plan artifacts contain no PAT; secret-bearing deployment output/errors are not printed.

On provisioning failure, the state records `provisioningStep` and the pipeline attempts to save a non-secret deployment-diagnostics artifact before cleanup. Diagnostics contain only deployment names, ARM error codes, and failed resource IDs/types. The CLI wrapper also extracts error codes from recognized error envelopes, including preflight failures that create no deployment history. Error messages, request bodies, credentials and deployment parameters remain suppressed because Azure errors can echo secure inputs.

Readiness retries are read-only and bounded. In addition to propagation/service status codes, only the specific `invalid_configuration` response that reports an agent-index listing timeout is retried; other configuration errors fail immediately. This does not prove a timeout is transient: persistent failures stop before pytest starts. The pipeline then attempts to capture run-owned Cosmos DB network settings, container names, data-role scopes and capability-host state before cleanup. No keys, connection credentials or document contents are queried. A sample that has already started is never retried automatically.

## API logs and print-output attachments

Each executed sample result includes two UTF-8 attachments in **Tests → select the test result → Attachments** (also available from its **Test Plans** result page):

- **API/print log**: the existing harness's success, validation-failure or execution-error log, including numbered HTTP request/response details and sample prints. The file retains its sample name, outcome suffix and timestamp.
- **Print-output log**: the existing sample output log, containing only captured `print()` calls without API entries.

[sample_ci_attachments.py](sample_ci_attachments.py) directs the shared synchronous/asynchronous executor's existing log writers to a separate node-ID-hashed directory per test under the run's **sample-results** artifact. It attaches those files directly, without copying, reformatting or sanitizing them again, using native JUnit `[[ATTACHMENT|path]]` markers in the result's `system-out`. **PublishTestResults** uploads the files for passing and failing tests; no additional ADO access token is passed to the test process. Attachment-publication errors fail the publication task.

The shared [sample log writer](../sample_log.py) redacts credential-shaped fields (authorization headers, tokens, API keys, cookies, signed URL parameters and known secret environment values) before any live sample log is written, including print-only output, validation reasons and exception details. Test Proxy's recording sanitizers apply to HTTP recordings, not these live files. The provisioning GitHub PAT remains absent from the test process. Oversized logs are replaced by an omission notice, not truncated across a possible credential. API bodies and print output can still contain sample data: use test data and the appropriate ADO access/retention settings; this is not a general-purpose personal-data filter.

The CI runner captures stdout/stderr rather than streaming raw sample prints with `-s`, and disables live log streaming. The plugin uses the shared redactor on captured reports and failure details before console/JUnit publication, even for samples without output validation. Attachment-like text printed by a test is neutralized; only the plugin's verified run-owned paths become upload markers. Validation still receives the original in-memory sample output.

Attachment capture is enabled only by the on-demand runner's explicit pytest plugin/option. Ordinary local live tests keep their temporary log-file location, now using the same redaction; playback still creates no live logs. For samples without LLM validation, the shared writer creates a capture-only log without claiming a validation result. If provisioning or readiness fails before the sample starts, there are no sample API/print attachments; the deployment/readiness diagnostics remain in **sample-results** instead. Historical test results are not modified; attachments appear on newly executed results.

## ADO Run pipeline: first sample

1. Open the configured pipeline in Azure DevOps and select **Run pipeline**.
2. Choose the branch containing this implementation. Ensure the pipeline's normal `AZURE_SUBSCRIPTION_ID` and `AZURE_TENANT_ID` variables are set to the intended subscription and tenant.
3. Set:
   - `runMode`: `preview` for the first check.
   - `selectionKind`: `sample-path`.
   - `selection`: the default, which targets [the requested synchronous MCP sample](../../../samples/agents/tools/sample_agent_mcp_with_project_connection.py).
4. Inspect the **Preview** log and **sample-plan** artifact. The selected test should be:

   `tests/samples/test_samples.py::TestSamples::test_agent_tools_samples[sample_agent_mcp_with_project_connection]`

5. Once the subscription/tenant/validation endpoint variables, secret GitHub PAT and target-authorized service connection are configured, run again with `runMode=run-and-cleanup`, the same selection, and that `azureServiceConnection`. Verify the target subscription, tenant, region and model in the preview. The pipeline automatically provisions, tests and cleans up after its preview succeeds; no **Review → Resume** action is required by this YAML.

Do not enter the PAT or validation endpoint into **Run pipeline** parameters. Those parameters are not secret fields.

### Approval behavior

- `preview` remains the default and cannot provision resources.
- `run-and-cleanup` explicitly opts in to automatic provisioning after a successful preview, including billable resources and ownership-checked cleanup. A failed preview prevents provisioning.
- Existing service-connection, environment, or organization-level approvals/checks are not changed or bypassed. ADO may still require those administrator-managed authorizations.
- Runs already queued retain their original YAML snapshot. Removing the manual stage affects only **new runs from the updated, pushed commit**; it does not resume or modify an existing paused run.

### Verify a second clean run

When repeatability is requested, first verify that the first test passed, its ownership-checked cleanup succeeded, and its final deployment state is `CleanedUp`. Only then queue one fresh run with the same reviewed subscription, tenant, region, model and selection. Generate a new plan and resource group; never reuse the first run's resources. Verify the second result and cleanup independently. Existing shared validation resources and separately approved permanent IAM grants are not removed by run-owned cleanup.

## Wildcard examples shown in the ADO UI

The `selectionKind` and `selection` display names include examples in **Run pipeline**.

| `selectionKind` | `selection` value | Result |
| --- | --- | --- |
| `sample-path` | `samples/agents/tools/sample_agent_mcp*project_connection*.py` | Requested sync and async MCP connection samples. |
| `sample-path` | `samples/agents/tools/*project_connection_async.py` | Async MCP connection sample. |
| `sample-path` | `samples/agents/sample_agent_basic*.py` | Basic sync and async agent samples. |
| `test-id` | `sample_agent_mcp_with_project_connection` | Only the requested sync sample parameter ID. |
| `test-id` | `sample_agent_mcp_with_project_connection*` | Sync and async parameter IDs. |
| `test-id` | `*test_agent_tools_samples*[*mcp*project_connection*]` | Matching full sync/async pytest node IDs. |
| `test-id` | `*test_samples_async.py::*[sample_agent_mcp_with_project_connection_async]` | The exact async case, with a wildcard test-file prefix. |
| `test-id` | `sample_agent_basic;sample_agent_mcp_with_project_connection` | Two exact parameter IDs, combined with OR. |

Rules:

- `*` matches zero or more characters, including path separators; `?` matches one character.
- Matching is case-insensitive; forward and backslashes are normalized.
- Brackets in pytest IDs are **literal**, not shell glob character classes. An exact full pytest node ID works without escaping its brackets.
- Semicolons or newlines separate OR patterns. Duplicate cases are removed and results are sorted.
- Sample paths are package-relative, starting with `samples/`. Repository-relative paths with the package prefix are also accepted.
- This is not pytest `-k` syntax: do not use `and`, `or`, shell expressions, or regular expressions.
- Only real collected harness cases are selectable. Samples excluded by `samples_to_skip` remain excluded; wildcard selection does not enable them.
- A broad wildcard may select samples needing other resource types. The preview rejects unsupported required environment variables **before provisioning**. This first implementation provisions Standard setup plus the GitHub MCP project connection, not every tool integration, hosted-agent image, dataset input, or fine-tuning prerequisite.

## Bicep sources and files

| File | Responsibility |
| --- | --- |
| [../../../tests.yml](../../../tests.yml) | ADO parameters, preview and automatic live-run stages, test results and always-run cleanup. |
| [infra/resource-group.bicep](infra/resource-group.bicep) | New resource group with exact CI ownership/expiry tags. |
| [infra/standard-setup.lock.json](infra/standard-setup.lock.json) | Official Standard setup commit and SHA-256 pin for all 14 Bicep source files. |
| [Get-StandardSetupTemplate.ps1](Get-StandardSetupTemplate.ps1) | Download those Bicep sources to agent temporary storage and fail on checksum mismatch. |
| [infra/sample-resources.bicep](infra/sample-resources.bicep) | Sample model deployment, runner roles and secure GitHub MCP connection; no validator provisioning. |
| [infra/sample-resources.bicepparam](infra/sample-resources.bicepparam) | Environment-backed Bicep inputs, including the secret PAT. |
| [New-SampleDeploymentPlan.ps1](New-SampleDeploymentPlan.ps1) | Offline fresh-plan generation and unsupported-input detection. |
| [Invoke-SampleProvisioning.ps1](Invoke-SampleProvisioning.ps1) | Read-only preflight, Bicep deployment orchestration, non-secret state and inventory. |
| [Remove-SampleResources.ps1](Remove-SampleResources.ps1) | Preview and apply cleanup only after exact resource-group ownership checks. |
| [select_samples.py](select_samples.py) | Wildcard selection against the real pytest collection. |
| [run_samples.py](run_samples.py) | Existing harness invocation, live/no-recording flags, non-secret environment mapping. |
| [sample_ci_attachments.py](sample_ci_attachments.py) | Per-test sanitized API/print files and native JUnit attachment markers. |

Standard setup is sourced from [the official Bicep template](https://github.com/microsoft-foundry/foundry-samples/tree/fbbe89b701c758e871922adaceea0ac0e4dae40f/infrastructure/infrastructure-setup-bicep/43-standard-agent-setup-with-customization). No precompiled upstream ARM JSON is used for provisioning. Update the commit and **every source checksum together** when adopting upstream changes. Do not edit downloaded files on an agent to work around a checksum or compilation error.

The pinned official template currently compiles with upstream Bicep warnings for capability-host schema metadata and optional AOAI references. The local templates compile without diagnostics. Compilation does not prove that the live subscription's policy, permissions or regional capacity will accept deployment.

### Regional dependency eligibility and quota

Before recording a deployment attempt, the live preflight checks:

- AI Search currently offers **S1** in the requested region, with available subscription service quota.
- Cosmos DB explicitly allows a new **non-zonal** account for this subscription in that region, matching the pinned template. A globally supported region can still be unavailable to an individual subscription.
- The pinned template's StorageV2 SKU is offered in the requested region without an applicable restriction: normally **Standard_ZRS**, or its upstream **Standard_GRS** fallback in South India and West US.

These are read-only checks. They do not choose a replacement region/SKU, register providers, attach existing resources, or guarantee deployment-time capacity. Missing or ambiguous eligibility evidence fails before resource-group creation. Consult the [Search offerings API](https://learn.microsoft.com/rest/api/searchmanagement/offerings/list), [Cosmos regional-access API](https://learn.microsoft.com/rest/api/cosmos-db-resource-provider/locations/list), and [Storage SKU API](https://learn.microsoft.com/rest/api/storagerp/skus/list) for their respective contracts.

An `InsufficientQuota` error on `Microsoft.CognitiveServices/accounts` while deploying Standard setup is an account-creation failure, not a sample-test or MCP authentication failure. Available model deployment capacity does not guarantee that another Foundry account can be created.

The live preflight separately checks `AccountCount` and the selected model SKU's exact catalog `usageName` in the [Cognitive Services regional usages API](https://learn.microsoft.com/rest/api/aiservices/accountmanagement/usages/list). Missing, duplicate, nonnumeric, negative or nonfinite quota values fail closed; exhausted or blocked quota stops before resource-group creation. These checks cannot cover every provider-specific limit or reserve capacity against concurrent runs. ARM validation can also pass before a deployment-time capacity failure.

Use a supported region with available account and model quotas, or ask the subscription administrator to review the applicable quota. Do not delete or purge existing accounts to make this test pass. Verify the preceding attempt's ownership-checked cleanup before queueing another live attempt.

## Cost, networking and cleanup limits

- Standard setup includes Storage **and** Cosmos DB **and** AI Search; these can incur standing charges even when a sample is idle. Application Insights is disabled for this initial MCP scenario.
- Resource colocation does not mean single-region inference: the default **GlobalStandard** model SKU can route inference globally. Review data-residency requirements before changing the topology or SKU.
- This is the official **public-network** Standard setup, not private-network isolation. Do not use production data. If policy forbids it, prepare a separately reviewed private-network variant instead of relaxing policy.
- All Standard setup resource-ID override parameters remain empty. This run creates new resources; it never attaches to a production project or shared production Storage account.
- Cleanup checks the task/plan/state subscription and tenant IDs, full resource-group ID, CI purpose, run ID and random owner token. It never adopts, retags, reuses, or deletes an existing group encountered during preflight.
- Cleanup failures fail the pipeline; the group must be confirmed absent before recording `CleanedUp`. `-WhatIf` never marks cleanup complete. The non-secret **sample-results** artifact includes state/inventory for administrator follow-up. Do not consider unrelated or unattributed resources safe to delete.
- `always()` and a cancellation grace period cannot guarantee cleanup after agent loss, hard termination, or control-plane errors. The expiry tag is **metadata, not an automatic deletion policy**. Administrators should monitor expired run-owned groups and review state/tags before removal.
- Foundry soft-deleted account records may remain after resource-group deletion. The pipeline does not purge them or weaken retention policies automatically.

## Local validation

### Offline regression checks

Use the package's configured virtual environment, installed Pester 4.10.1 and repository Black configuration. These checks do not run service tests, load local dotenv values or require Azure credentials:

- Run the unit tests under this directory with `--confcutdir=tests/samples/ci` to avoid parent service fixtures.
- Run all `*.Tests.ps1` files in this directory with Pester. They cover explicit target IDs, application/tenant consistency, regional eligibility, quota values, log-safe diagnostics, default plan generation, and actual cleanup behavior with an isolated fake Azure CLI.
- With the Bicep compiler and pinned sources already available locally, run [Test-BicepTemplates.ps1](Test-BicepTemplates.ps1). It verifies exactly one sample model and no validation deployment or endpoint output, using fictional bindings and an empty PAT.
- For harness collection and plan generation, set `PYTHON_DOTENV_DISABLED=true` and supply fictional target IDs through the environment. Collect with [select_samples.py](select_samples.py); collection must not execute samples.

### Networked checks without provisioning

- Installing the pinned Pester release and development packages requires their package feeds.
- [Get-StandardSetupTemplate.ps1](Get-StandardSetupTemplate.ps1) downloads integrity-pinned sources from GitHub to temporary storage; downloading is not an offline check.
- ADO YAML expansion with `previewRun=true` requires authorization. **Modified-YAML previews require pipeline edit permission**; queue permission alone is insufficient. Do not queue a live run as a workaround for a denied preview.

### Live validation

Run `run-and-cleanup` only after the service connection, explicit target variables and shared-validator permissions are configured. A local deployment under a developer's identity does not validate CI permissions or the selected sample. Verify the selected sample result, attachment publication and run-owned cleanup together; retain that run-specific evidence in the PR or pipeline results rather than this guide.
