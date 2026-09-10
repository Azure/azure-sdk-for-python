# Agent Insights samples and tests

Both samples are self-contained. Each invocation registers a uniquely named
temporary external agent, emits eight fictional defect traces and two control
traces, and waits for all root, chat, and tool spans to reach Application Insights.
No real tool or inference call produces the seed data. The on-demand sample
then runs analysis, reads results, and resolves an insight. The scheduled sample
sets a six-hour interval and reads the next run time; it does not wait for analysis.

The external agent is a metadata registration, not a deployed agent process.
Each sample uses a local tracing provider, flushes it, and shuts it down without
changing global telemetry configuration.

## Existing-resource prerequisites

Use a project in a region where Agent Insights is available, with:

- A connected Application Insights resource.
- A suitable analysis-model deployment accessible to the project.
- An identity that can create/delete agents and monitors, read the connected
  telemetry configuration, ingest telemetry, and query Application Insights.
- A project managed identity with model access and access to query trace content.
  When content is stored in the protected `AppGenAIContent` table, this includes
  **Privileged Monitoring Data Reader** at the Application Insights resource scope
  in addition to the required read/query access.

The samples do not provision resources, models, or role assignments, and do not
wait for permission changes to propagate. Authentication and query failures
surface immediately. Missing prerequisites must be resolved before execution.

Set these values in the environment or the ignored package `.env` file:

```text
FOUNDRY_PROJECT_ENDPOINT=<existing-project-endpoint>
FOUNDRY_MODEL_NAME=<analysis-model-deployment-name>
AGENT_INSIGHTS_APPLICATION_INSIGHTS_RESOURCE_ID=<connected-application-insights-resource-id>
```

Do not supply an existing agent name or OpenTelemetry agent ID. The samples get
the connection string through the public project telemetry client and do not
print it. Each unique agent ID also isolates its trace batch.

From `sdk/ai/azure-ai-projects`, with Python 3.10+:

```bash
python -m pip install -e . -r dev_requirements.txt
python samples/agent_insights/sample_agent_insights_on_demand.py
python samples/agent_insights/sample_agent_insights_scheduled.py
```

Ingestion is checked for up to five minutes. A successful sample should normally
take less than ten minutes, but ingestion and analysis depend on service load.
This is not a global execution deadline.

## Cleanup

Both samples use `finally`, including after setup or analysis failure. They only
delete resources they created: first disable the monitor, cancel any active
runs, and delete the monitor; then delete the external agent. Cleanup checks at
most 12 times with 10 seconds between checks. Enabling a schedule can start a run
immediately, so scheduled cleanup may need to cancel that run.

If monitor cleanup fails, the agent is retained to preserve the dependency order.
Resource identifiers are printed for manual cleanup. Service failures, missing
permissions, or forced process termination can leave resources behind. Later
invocations use new names and do not change those leftovers.

Deleting the monitor and external-agent registration does not purge ingested
telemetry. The fictional traces remain under normal Application Insights retention.

## Tests and recording refresh

Run the focused offline unit tests from the package directory:

```bash
AZURE_TEST_RUN_LIVE=false python -m pytest -q tests/agent_insights
```

The recorded entry points remain in `tests/samples/test_samples.py`, using the
existing sample executor, Test Proxy, and playback sleep fixture. Output checks
verify agent/monitor ownership and deletion, successful on-demand analysis and
resolution, and the six-hour schedule without a second model call.

**The existing recordings predate this lifecycle. Their refresh is deferred.**
They do not yet cover registration, connection lookup, export, ingestion queries,
or agent deletion. Do not treat old playback as proof of the redesigned samples.
No asset pointer is changed in this iteration.

When a maintainer refreshes recordings against the prepared existing resources:

```bash
AZURE_TEST_RUN_LIVE=true python -m pytest -q \
    tests/samples/test_samples.py::TestSamples::test_agent_insights_samples
```

No separate provisioning fixture is needed. Record both complete lifecycles and
check all exporter traffic, including background work, routes through Test Proxy.
Inspect recordings for secrets and live identifiers, including connection
strings, resource IDs, generated agent names, and telemetry payloads. Then publish
with the normal repository recording workflow and replay with
`AZURE_TEST_RUN_LIVE=false`. Playback must not need Azure credentials or send
telemetry to Azure.

Repository recording guide:
https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/tests.md#update-test-recordings

SDK design guidance:
https://azure.github.io/azure-sdk/python_design.html
