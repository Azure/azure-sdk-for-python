# Agent Insights recording fixture

This fixture is for SDK maintainers. Customer samples use an existing agent;
they do not deploy resources or create trace data. Normal PR tests use recorded
HTTP responses and do not call Azure.

## Prepare the environment

Use a subscription and region where the current Agent Insights API is available.
The deployment identity must be able to create Foundry and telemetry resources,
assign roles, and read keys from the existing analysis-model account. The template
creates the required roles by default.

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
    -TestResourcesDirectory sdk/ai/azure-ai-projects `
    -SubscriptionId "<test-subscription-id>" `
    -TestApplicationOid "<test-identity-object-id>" `
    -ResourceGroupName "<disposable-resource-group>" `
    -BaseName "<unique-test-name>" `
    -Location "<supported-region>" `
    -AdditionalParameters $model `
    -OutFile
```

The script writes an ignored `.env` file in the package directory. It contains
the project endpoint, external-agent name, analysis-model name, and telemetry
resource IDs. Use the same test identity for the following steps, authenticated
through Azure CLI or Azure PowerShell.

## Create trace data and record the samples

From `sdk/ai/azure-ai-projects`, with a Python 3.10+ virtual environment active:

```bash
python -m pip install -e . -r dev_requirements.txt
python tests/agent_insights/recording_fixture.py
```

The helper creates or reuses one external-agent version. It emits eight
fictional destructive-tool traces and two non-destructive control traces, then
waits until all ten are queryable. No tool is actually executed. Run this helper
again before refreshing recordings; the on-demand sample analyzes a recent
three-hour window.

Record both samples:

```bash
AZURE_TEST_RUN_LIVE=true python -m pytest -q \
    tests/samples/test_samples.py::TestSamples::test_agent_insights_samples
```

The on-demand recording must show a successful run with at least one analyzed
trace and one insight, then a resolved and reopened insight. The scheduled
sample checks the schedule without waiting for analysis. Both samples delete
their monitors; scheduled cleanup disables the schedule and cancels any active
run first.

Review the recordings for secrets and live identifiers before publishing:

```bash
python ../../../../scripts/manage_recordings.py locate
python ../../../../scripts/manage_recordings.py push
python -m pytest -q tests/samples/test_samples.py::TestSamples::test_agent_insights_samples
```

The last command must run with `AZURE_TEST_RUN_LIVE` unset or set to `false`.
Commit the updated `assets.json`, not the `.env` file. Delete the disposable
resource group when finished. This removes the fixture agent and telemetry
resources; the external analysis-model account is not part of that group.

Repository recording guide:
https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md#update-test-recordings
