# Azure AI Agent Server A2A client library for Python

The `azure-ai-agentserver-a2a` package hosts a native A2A v1.0
[`a2a-sdk`](https://pypi.org/project/a2a-sdk/) handler in an Azure AI Hosted
Agent container. It adds Foundry's hosting contract while leaving the agent
card, executor, request handler, and task store in the native A2A SDK.

The package is optional: customers can implement the documented Foundry
container contract themselves. It is the recommended convenience layer because
it reduces the required route, lifecycle, telemetry, and request-context glue
to a small host declaration. The container contract itself remains mandatory.

## Getting started

### Install the package

```bash
pip install azure-ai-agentserver-a2a
```

### Build and install an alpha

Alpha packages use the same internal dev-feed workflow as the Activity host.
They are not published to PyPI.

1. Commit and push the A2A and core changes to a branch available to the
   [internal `python - agentserver` pipeline](https://dev.azure.com/azure-sdk/internal/_build?definitionId=7974).
   A fork-only branch must first be made available to that pipeline's source
   repository by a maintainer.
2. Select **Run pipeline**, choose that branch, and enable
   **Publish A2A and core alpha packages to the dev feed** (`PublishA2AAlpha`).
3. Keep **Build** and **Integration** selected. The opt-in applies only to
   internal manual runs; it sets `SetDevVersion=true` and `Skip.Release=true`.
   Leave the `BuildTargetingString` variable unset so neither package is
   filtered out. Normal CI, scheduled builds, and PR validation are unchanged.
4. Check the Integration job's publish steps for both
   `azure-ai-agentserver-a2a` and `azure-ai-agentserver-core`. Normal validation
   still covers the service packages, but this mode publishes only these two
   alpha packages, not the other Agent Server hosts.

The pipeline generates versions from its build number without changing the
checked-in versions. For example, build `20261021.1` produces
`1.0.0a20261021001` (A2A) and `2.2.1a20261021001` (core).
Replace the example versions below with those from the successful run:

```powershell
python -m pip install --pre `
  --index-url "https://pkgs.dev.azure.com/azure-sdk/public/_packaging/azure-sdk-for-python/pypi/simple/" `
  "azure-ai-agentserver-a2a==1.0.0a20261021001" `
  "azure-ai-agentserver-core==2.2.1a20261021001"
```

Install both packages from the same run to include the core tracing enrichment
changes. The dev-build tooling rewrites A2A's core dependency to an alpha range;
pinning both versions also prevents accidentally testing a different core build.
Regular preview installations require core 2.2.1 or later, which contains the
Agent Card metadata-preservation fix.

### Prerequisites

- Python 3.10 or later
- A native A2A v1.0 `AgentCard` and `RequestHandler`

## Key concepts

### A2AAgentServerHost

`A2AAgentServerHost` is an `AgentServerHost` subclass that:

- registers the native JSON-RPC handler at `POST /a2a`;
- accepts `POST /invocations/a2a` as a non-advertised compatibility alias for
  Foundry service versions that still forward to the legacy container path;
- registers the native public agent card at
  `GET /a2a/.well-known/agent-card.json`;
- captures `x-agent-foundry-call-id` and `x-agent-user-id` in the
  request-scoped Foundry context;
- provides `/readiness`, port configuration, telemetry, and graceful shutdown
  through `azure-ai-agentserver-core`.

  Both POST routes execute the same native handler and semantic tracing wrapper.

The Foundry passthrough advertises only the JSON-RPC binding, including
`SendStreamingMessage` responses over SSE. Push notifications, the authenticated
extended card, HTTP+JSON/REST, and gRPC are not exposed in the initial release.

### Distributed tracing

The host emits one `SERVER` span for each valid A2A JSON-RPC operation using
the `Azure.AI.AgentServer.A2A` instrumentation scope. Span names are the A2A
method names (`SendMessage`, `SendStreamingMessage`, `GetTask`, and so on).
Attributes include protocol, message, task, Agent Card, and `contextId`
correlation data. JSON-RPC errors set `error.type` and mark the span as failed
even though the HTTP response status is 200. Streaming spans remain open until
the SSE response completes.

These attributes follow the development-stage proposal in
[OpenTelemetry GenAI semantic conventions PR 195](https://github.com/open-telemetry/semantic-conventions-genai/pull/195)
and may evolve before that convention becomes stable.

The native `a2a-sdk` currently emits generic implementation-level spans in
addition to these semantic operation spans. To avoid duplicate server spans,
set this environment variable **before importing `a2a`**:

```bash
OTEL_INSTRUMENTATION_A2A_SDK_ENABLED=false
```

## Examples

### Host a native A2A application

```python
from azure.ai.agentserver.a2a import A2AAgentServerHost

host = A2AAgentServerHost(agent_card=card, request_handler=handler)
host.run()
```

The package intentionally does not replace the native A2A SDK. Continue using
native A2A types for the agent card, executor, handler, task store, messages,
artifacts, and tasks.

### Call a Foundry service from an A2A handler

The host binds the inbound platform identity to a `ContextVar`. Forward the
call ID, in addition to normal authorization, when custom code calls a service
under `FOUNDRY_PROJECT_ENDPOINT`:

```python
from azure.ai.agentserver.core import get_request_context

headers = {
    "Authorization": bearer,
    **get_request_context().platform_headers(),
}
await client.post(foundry_service_url, headers=headers, json=payload)
```

`platform_headers()` forwards only `x-agent-foundry-call-id`. The inbound user
ID remains available as `get_request_context().user_id` for container-side
state partitioning and is not forwarded to Foundry services.

An inbound A2A `contextId` is recorded as `gen_ai.conversation.id` and added to
the active baggage context so child model, tool, and framework spans can use the
same conversation correlation.

### Host A2A and Invocations together

Protocol hosts use cooperative inheritance, so both protocols can share one
process and port:

```bash
pip install azure-ai-agentserver-a2a azure-ai-agentserver-invocations
```

```python
from azure.ai.agentserver.a2a import A2AAgentServerHost
from azure.ai.agentserver.invocations import InvocationAgentServerHost


class MultiProtocolHost(A2AAgentServerHost, InvocationAgentServerHost):
    pass


host = MultiProtocolHost(agent_card=card, request_handler=handler)


@host.invoke_handler
async def handle_invocation(request):
    ...


host.run()
```

See the [samples directory](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-a2a/samples)
for standalone and multi-protocol examples.

## Scope

This package hosts incoming A2A traffic. It does not provide an outbound A2A
client or intercept calls from the hosted agent to another agent.

The Foundry service rewrites the externally returned agent card. Container
security schemes, signatures, provider/branding fields, internal URLs, and
unsupported capabilities are not exposed to callers.

## Contributing

This project welcomes contributions and suggestions. Most contributions
require you to agree to a Contributor License Agreement (CLA) declaring that
you have the right to, and actually do, grant us the rights to use your
contribution. For details, visit [https://cla.microsoft.com](https://cla.microsoft.com).

This project has adopted the
[Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
