# Agent Insights recording fixture

This fixture is for SDK maintainers. Customer samples use an existing agent;
they do not deploy resources or create trace data. Normal PR tests use recorded
HTTP responses and do not call Azure.

Agent Insights unit tests, sample-output checks, and recording setup live in
this directory. The shared sample runner remains in `tests/samples/` so existing
recording paths do not change. The optional Azure deployment files are in
`resources/`; they are not a general test environment for the package.

From the package directory, run the offline tests and recorded samples with:

```bash
AZURE_TEST_RUN_LIVE=false python -m pytest -q tests/agent_insights \
    tests/samples/test_samples.py::TestSamples::test_agent_insights_samples
```

## Prepare the environment

Use a subscription and region where the current Agent Insights API is available.
The deployment identity must be able to create Foundry and telemetry resources,
assign roles, and read keys from the existing analysis-model account. The template
creates Foundry User and Monitoring Reader assignments by default. Protected
trace content requires the additional assignment described below.

An existing analysis-model deployment is required. The template defaults to
GPT-5.4, model version `2026-03-05`, and the `GlobalStandard` SKU. The
post-deployment hook checks those values with the authenticated Azure PowerShell
context. It does not install Python packages or run the fixture.

From the repository root, use the standard test-resource script. Supply your own
resource names and IDs; do not commit them:

```powershell
Connect-AzAccount

$model = @{
    analysisModelSubscriptionId = "<model-subscription-id>"
    analysisModelResourceGroupName = "<model-resource-group>"
    analysisModelAccountName = "<model-account>"
    analysisModelDeploymentName = "<model-deployment>"
}

./eng/common/TestResources/New-TestResources.ps1 `
    -ServiceDirectory ai `
    -TestResourcesDirectory sdk/ai/azure-ai-projects/tests/agent_insights/resources `
    -SubscriptionId "<test-subscription-id>" `
    -TestApplicationOid "<test-identity-object-id>" `
    -ResourceGroupName "<disposable-resource-group>" `
    -BaseName "<unique-test-name>" `
    -Location "<supported-region>" `
    -AdditionalParameters $model `
    -OutFile
```

The script writes an ignored `.env` file beside the template in
`tests/agent_insights/resources/`. It contains the project endpoint,
external-agent name, analysis-model name, and telemetry resource IDs. Copy those
settings into the package-level `.env` file without replacing unrelated
settings. Use the same test identity for the following steps, authenticated
through Azure CLI or Azure PowerShell.

### Access to protected trace content

If the connected Application Insights resource uses the protected
`AppGenAIContent` table, grant **Privileged Monitoring Data Reader** to the
Foundry project's managed identity at the **Application Insights resource**
scope. Use the project's principal ID, not the parent account's identity or the
identity running the sample. Keep its existing read/query role: Monitoring
Reader and Privileged Monitoring Data Reader provide different permissions.

An administrator authorized to create role assignments at that resource can run:

```bash
az role assignment create \
    --assignee-object-id "<project-managed-identity-principal-id>" \
    --assignee-principal-type ServicePrincipal \
    --role "Privileged Monitoring Data Reader" \
    --scope "<application-insights-resource-id>"
```

Use the resource scope, not the subscription scope. If the command fails with
`Microsoft.Authorization/roleAssignments/write`, an authorized role
administrator must apply it, or the operator must activate an existing eligible
administrative role. Allow the assignment to propagate before retrying.

This grant lets the service read protected message/tool content; it does not
grant the maintainer's own identity access to that content. Trace spans can be
queryable while their referenced protected content is unavailable. A query
returning no content rows does not by itself distinguish missing ingestion from
missing access.

## Create trace data and record the samples

From `sdk/ai/azure-ai-projects`, with a Python 3.10+ virtual environment active:

```bash
python -m pip install -e . -r dev_requirements.txt
python tests/agent_insights/recording_fixture.py
```

The helper creates or reuses one external-agent version. It emits eight
fictional destructive-tool traces and two non-destructive control traces that
decline to guess workspace status without a read tool. It waits until all ten
traces, including their chat and tool spans, are queryable. No tool is actually
executed. Run this helper again before refreshing recordings; the on-demand
sample analyzes a recent three-hour window.

Record both samples:

```bash
AZURE_TEST_RUN_LIVE=true python -m pytest -q \
    tests/samples/test_samples.py::TestSamples::test_agent_insights_samples
```

The on-demand recording must show a successful run with at least one analyzed
trace and one insight, then a resolved and reopened insight. The scheduled
sample checks the schedule without waiting for analysis. Both samples disable
scheduling, cancel any active run, and delete their monitors during cleanup.

Tests check these outcomes directly from the sample output. They do not call a
second model or require Code Interpreter to validate the samples.

Review the recordings for secrets and live identifiers before publishing:

```bash
python ../../../scripts/manage_recordings.py locate
python ../../../scripts/manage_recordings.py push
python -m pytest -q tests/samples/test_samples.py::TestSamples::test_agent_insights_samples
```

The last command must run with `AZURE_TEST_RUN_LIVE` unset or set to `false`.
Commit the updated `assets.json`, not the `.env` file. Delete the disposable
resource group when finished. This removes the fixture agent and telemetry
resources; the external analysis-model account is not part of that group.

Repository recording guide:
https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md#update-test-recordings
