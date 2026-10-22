# On-demand sample tests in Azure DevOps

[../../../tests.yml](../../../tests.yml) runs the existing synchronous and asynchronous pytest sample harness against a new, temporary **Standard Foundry project**. Provisioning uses **Bicep**, not imperative resource-creation scripts.

The first-run default is [../../../samples/agents/tools/sample_agent_mcp_with_project_connection.py](../../../samples/agents/tools/sample_agent_mcp_with_project_connection.py). The same selector can choose its async counterpart or other collected sample tests.

## What happens

1. Collect the real cases in [../test_samples.py](../test_samples.py) and [../test_samples_async.py](../test_samples_async.py). Do not execute samples during collection.
2. Match the sample-path or test-ID wildcard and show the exact selected cases. Zero matches fail; the pipeline never falls back to all tests.
3. Generate a non-secret provisioning plan, download integrity-pinned official Standard setup **Bicep sources**, and compile all templates. The default `preview` mode ends here and makes no Azure changes.
4. In `run-and-cleanup` mode, continue automatically after this run's fresh preview succeeds. There is no YAML manual-approval stage. Selecting this mode when queueing explicitly opts in to creating billable resources and deleting this run's temporary resources afterward.
5. Authenticate with the authorized Azure Resource Manager service connection. Check provider registration, model availability, Cognitive Services `AccountCount` quota, and model-deployment quota before creating a resource group, then deploy Bicep to create:
   - A uniquely named, run-owned resource group.
   - A Foundry account and project with managed identities.
   - A Storage account, Cosmos DB account, AI Search service, project connections, capability hosts and runtime role assignments: the official **Standard agent setup**.
   - The selected sample model and **gpt-5.2**, which the existing sample harness uses to validate console output. If the sample model is also gpt-5.2, only one matching deployment is created.
   - A project-scoped GitHub MCP connection when the selected sample requires `MCP_PROJECT_CONNECTION_ID`.
6. Wait for project/RBAC readiness, then run only the selected pytest node IDs with live mode on and recording off. Publish JUnit results to the ADO **Tests** tab.
7. Run cleanup even after failure or cancellation, verifying the resource-group ID and every ownership tag before deleting **only this run's temporary resource group**. Capture non-secret resource inventories before/after deployment.

PowerShell orchestrates Bicep and cleanup; Python collects and invokes the existing tests. Neither provisions Azure resources imperatively. Cleanup is necessarily a resource-group deletion rather than a Bicep deployment.

## One-time administrator setup

### Pipeline and Azure access

- Existing pipeline **8392**, `python - azure-ai-projects - tests`, references the package's [../../../tests.yml](../../../tests.yml). Publish this branch through the normal review process, then select that branch in **Run pipeline**. No definition update is needed if its YAML path is unchanged.
- An administrator must make an **Azure Resource Manager service connection** available to this pipeline; **workload identity federation** is recommended. Enter its name in `azureServiceConnection`.
- Provisioning creates a new resource group, so the connection needs subscription-level resource-group/deployment permissions plus management and role-assignment permissions on the new resources. Use an administrator-approved role configuration, for example **Contributor + Role Based Access Control Administrator**, rather than granting the pipeline unrestricted access to unrelated resources. Merely having Foundry User is insufficient to provision Standard setup.
- Register `Microsoft.CognitiveServices`, `Microsoft.Storage`, `Microsoft.DocumentDB`, and `Microsoft.Search` in advance. Preflight fails rather than registering providers automatically.
- Ensure the selected region supports Standard Foundry, Cosmos DB, Search, and both requested model deployments with sufficient quota. Default region: `eastus2`. `auto` model versions resolve from the regional catalog; pin explicit versions when reproducibility requires it.
- Authorize the pipeline's use of the Azure SDK package feed and the `azsdk-pool` agent pool. The pipeline reuses the repository's 1ES template and feed-authentication steps. The feed supplies the development-only resource detector dependency.

Current access limitations are independent: permission to **queue** pipeline 8392 does not imply permission to **edit** it, preview modified YAML, save pipeline secrets, create Library groups, or authorize a service connection. Ask a pipeline/Library administrator for the necessary setup; do not change identities or bypass those controls.

### Save the GitHub PAT as a secret

The MCP service is GitHub, so this is a **GitHub PAT**, not an Azure DevOps PAT.

Choose one supported storage location:

1. **Pipeline secret**: a pipeline administrator opens **Pipelines → this pipeline → Edit → Variables → New variable**, sets the name to `MCP_GITHUB_PAT`, enters the **complete token including its prefix** (`github_pat_…` or `ghp_…`), checks **Keep this value secret**, and saves. Leave `secretVariableGroup=none`.
2. **Library secret**: a Library administrator creates or updates an approved variable group, adds `MCP_GITHUB_PAT` with its **lock/secret setting enabled**, and authorizes only the intended pipeline. Set `secretVariableGroup` to that group's name.

Enter the value **directly in the ADO secret field**. Do not paste it into chat, YAML, runtime parameters, source control, artifacts, or logs. Do not assume pipeline-variable editing is available to a user who lacks pipeline edit permission.

Use the minimum GitHub token permissions needed by the MCP tools this sample calls, a short expiration, and any required organization/SSO authorization. The sample queries the authenticated GitHub profile; do not grant repository write permissions merely to run this test. Refer to [GitHub MCP authentication guidance](https://github.com/github/github-mcp-server/blob/main/docs/remote-server.md) for current token support and requirements.

Only the provisioning task receives `MCP_GITHUB_PAT`. [infra/sample-resources.bicepparam](infra/sample-resources.bicepparam) reads it from the process environment and supplies the Bicep `@secure()` parameter. The connection stores `Authorization = Bearer <complete-token>`, category `RemoteTool`, authentication `CustomKeys`, metadata `type=custom_MCP`, and `isSharedToAll=false`.

This matches the connection contract in the supplied project-pool reference, but **does not blindly prepend `github_pat_`**. Supplying a full token avoids a duplicate token prefix. The test process receives the **connection resource ID**, never the PAT. Deployment-state and plan artifacts contain no PAT; secret-bearing deployment output/errors are not printed.

On provisioning failure, the state records `provisioningStep` and the pipeline attempts to save a non-secret deployment-diagnostics artifact before cleanup. Diagnostics contain only deployment names, ARM error codes, and failed resource IDs/types. Error messages, request bodies, credentials and deployment parameters remain suppressed because Azure errors can echo secure inputs.

## ADO Run pipeline: first sample

1. Open [pipeline 8392](https://dev.azure.com/azure-sdk/internal/_build?definitionId=8392) and select **Run pipeline**.
2. Choose the branch containing this implementation.
3. Set:
   - `runMode`: `preview` for the first check.
   - `selectionKind`: `sample-path`.
   - `selection`: the default, which targets [the requested synchronous MCP sample](../../../samples/agents/tools/sample_agent_mcp_with_project_connection.py).
4. Inspect the **Preview** log and **sample-plan** artifact. The selected test should be:

   `tests/samples/test_samples.py::TestSamples::test_agent_tools_samples[sample_agent_mcp_with_project_connection]`

5. Once secret/service-connection setup is complete, run again with `runMode=run-and-cleanup`, the same selection, and your authorized `azureServiceConnection`. The pipeline automatically provisions, tests and cleans up after its preview succeeds; no **Review → Resume** action is required by this YAML.

Do not enter the PAT into **Run pipeline** parameters. Those parameters are not secret fields.

### Approval behavior

- `preview` remains the default and cannot provision resources.
- `run-and-cleanup` explicitly opts in to automatic provisioning after a successful preview, including billable resources and ownership-checked cleanup. A failed preview prevents provisioning.
- Existing service-connection, environment, or organization-level approvals/checks are not changed or bypassed. ADO may still require those administrator-managed authorizations.
- Runs already queued retain their original YAML snapshot. Removing the manual stage affects only **new runs from the updated, pushed commit**; it does not resume or modify an existing paused run.

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
| [infra/sample-resources.bicep](infra/sample-resources.bicep) | Model deployments, runner roles and secure GitHub MCP connection. |
| [infra/sample-resources.bicepparam](infra/sample-resources.bicepparam) | Environment-backed Bicep inputs, including the secret PAT. |
| [New-SampleDeploymentPlan.ps1](New-SampleDeploymentPlan.ps1) | Offline fresh-plan generation and unsupported-input detection. |
| [Invoke-SampleProvisioning.ps1](Invoke-SampleProvisioning.ps1) | Read-only preflight, Bicep deployment orchestration, non-secret state and inventory. |
| [Remove-SampleResources.ps1](Remove-SampleResources.ps1) | Preview and apply cleanup only after exact resource-group ownership checks. |
| [select_samples.py](select_samples.py) | Wildcard selection against the real pytest collection. |
| [run_samples.py](run_samples.py) | Existing harness invocation, live/no-recording flags, non-secret environment mapping. |

Standard setup is sourced from [the official Bicep template](https://github.com/microsoft-foundry/foundry-samples/tree/fbbe89b701c758e871922adaceea0ac0e4dae40f/infrastructure/infrastructure-setup-bicep/43-standard-agent-setup-with-customization). No precompiled upstream ARM JSON is used for provisioning. Update the commit and **every source checksum together** when adopting upstream changes. Do not edit downloaded files on an agent to work around a checksum or compilation error.

The pinned official template currently compiles with upstream Bicep warnings for capability-host schema metadata and optional AOAI references. The local templates compile without diagnostics. Compilation does not prove that the live subscription's policy, permissions or regional capacity will accept deployment.

### Account quota versus model quota

An `InsufficientQuota` error on `Microsoft.CognitiveServices/accounts` while deploying Standard setup is an account-creation failure, not a sample-test or MCP authentication failure. Available model deployment capacity does not guarantee that another Foundry account can be created.

The live preflight separately checks the `AccountCount` entry from the [Cognitive Services regional usages API](https://learn.microsoft.com/rest/api/aiservices/accountmanagement/usages/list), logs its non-secret used/limit values, and stops before resource-group creation if that quota is exhausted, blocked or unverifiable. This check cannot cover every provider-specific limit or reserve capacity against concurrent runs; ARM validation remains authoritative.

Use a supported region with available account and model quotas, or ask the subscription administrator to review the applicable quota. Do not delete or purge existing accounts to make this test pass. Verify the preceding attempt's ownership-checked cleanup before queueing another live attempt.

## Cost, networking and cleanup limits

- Standard setup includes Storage **and** Cosmos DB **and** AI Search; these can incur standing charges even when a sample is idle. Application Insights is disabled for this initial MCP scenario.
- This is the official **public-network** Standard setup, not private-network isolation. Do not use production data. If policy forbids it, prepare a separately reviewed private-network variant instead of relaxing policy.
- All Standard setup resource-ID override parameters remain empty. This run creates new resources; it never attaches to a production project or shared production Storage account.
- Cleanup checks the full resource-group ID, CI purpose, run ID and random owner token. It never adopts, retags, reuses, or deletes an existing group encountered during preflight.
- Cleanup failures fail the pipeline; the non-secret **sample-results** artifact includes state/inventory for administrator follow-up. Do not consider unrelated or unattributed resources safe to delete.
- `always()` and a cancellation grace period cannot guarantee cleanup after agent loss, hard termination, or control-plane errors. The expiry tag is **metadata, not an automatic deletion policy**. Administrators should monitor expired run-owned groups and review state/tags before removal.
- Foundry soft-deleted account records may remain after resource-group deletion. The pipeline does not purge them or weaken retention policies automatically.

## Local offline validation

Use the package's configured virtual environment and repository Black configuration. These checks do not run service tests:

- Run the unit tests under this directory with `--confcutdir=tests/samples/ci` to avoid parent service fixtures.
- Run [SampleCiHelpers.Tests.ps1](SampleCiHelpers.Tests.ps1) with Pester for ownership, PAT-shape, model/account preflight, and secret-safe error-diagnostic tests.
- Fetch pinned Bicep sources to temporary storage and run [Test-BicepTemplates.ps1](Test-BicepTemplates.ps1); its parameter compilation uses fictional values and an empty PAT.
- Collect [../test_samples.py](../test_samples.py) and [../test_samples_async.py](../test_samples_async.py) with [select_samples.py](select_samples.py), then generate an offline plan.
- Request ADO YAML expansion with `previewRun=true` only if authorized. **Modified-YAML previews require pipeline edit permission**; queue permission alone is insufficient. Do not queue a live run as a workaround for a denied preview.

Live sample execution and resource deployment remain unverified until an authorized live pipeline run succeeds.
