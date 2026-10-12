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

### Prerequisites

- Python 3.10 or later
- A native A2A v1.0 `AgentCard` and `RequestHandler`

## Key concepts

### A2AAgentServerHost

`A2AAgentServerHost` is an `AgentServerHost` subclass that:

- registers the native JSON-RPC handler at `POST /invocations/a2a`;
- registers the native public agent card at
  `GET /invocations/a2a/.well-known/agent-card.json`;
- captures `x-agent-foundry-call-id`, `x-agent-user-id`, and
  `x-agent-session-id` in the request-scoped Foundry context;
- provides `/readiness`, port configuration, telemetry, and graceful shutdown
  through `azure-ai-agentserver-core`.

The Foundry passthrough advertises only the JSON-RPC binding. Streaming, push
notifications, the authenticated extended card, HTTP+JSON/REST, and gRPC are
not exposed in the initial release.

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
