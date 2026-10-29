# Azure AI Agent Server A2A client library for Python

The `azure-ai-agentserver-a2a` package hosts a native A2A v1.0
[`a2a-sdk`](https://pypi.org/project/a2a-sdk/) handler in an Azure AI Hosted
Agent container. It adds Foundry's hosting contract while leaving the agent
card, executor, request handler, and protocol semantics in the native A2A SDK.
It can also persist native Tasks using Core's existing Foundry state store.

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
checked-in versions. For example, build `20261028.1` produces
`1.0.0a20261028001` (A2A) and `2.3.0a20261028001` (core).
Replace the example versions below with those from the successful run:

```powershell
python -m pip install --pre `
  --index-url "https://pkgs.dev.azure.com/azure-sdk/public/_packaging/azure-sdk-for-python/pypi/simple/" `
  "azure-ai-agentserver-a2a==1.0.0a20261028001" `
  "azure-ai-agentserver-core==2.3.0a20261028001"
```

Install both packages from the same run to include the core tracing enrichment
changes. The dev-build tooling rewrites A2A's core dependency to an alpha range;
pinning both versions also prevents accidentally testing a different core build.
Regular preview installations require core 2.3.0b3 or later, which contains the
Agent Card metadata-preservation fix.

### Prerequisites

- Python 3.10 or later
- `a2a-sdk>=1.2.3,<2.0.0`, which includes owner authorization on active-task
  cache hits used by subscription and cancellation
- A native A2A v1.0 `AgentCard` and either an `AgentExecutor` or `RequestHandler`

## Key concepts

### A2AAgentServerHost

`A2AAgentServerHost` is an `AgentServerHost` subclass that:

- registers the native JSON-RPC handler at `POST /a2a`;
- accepts `POST /invocations/a2a` and
  `GET /invocations/a2a/.well-known/agent-card.json` as non-advertised
  compatibility aliases for older Foundry service versions and clients;
- registers the native public agent card at
  `GET /a2a/.well-known/agent-card.json`;
- captures `x-agent-foundry-call-id` and `x-agent-user-id` in the
  request-scoped Foundry context;
- provides `/readiness`, port configuration, telemetry, and graceful shutdown
  through `azure-ai-agentserver-core`.
- builds a native default request handler when given an executor, selecting
  Foundry-backed task storage when hosted and native in-memory storage locally.

  Both POST routes execute the same native handler and semantic tracing wrapper.
  Both card routes use the same native card handler and `card_modifier`; the
  compatibility alias does not rewrite the card or advertise an extra interface.

The Foundry passthrough advertises only the JSON-RPC binding. Push notifications,
the authenticated extended card, HTTP+JSON/REST, and gRPC are not exposed in the
initial release.

### Distributed tracing

In Foundry-hosted environments, `SendMessage` also emits one `invoke_agent`
parent span using the deployed Foundry agent name,
version, and identity. This keeps hosted-agent trace discovery independent of
LLM calls or native SDK implementation spans. The child A2A operation span
retains Agent Card metadata, which can differ from the deployment name/version.
Both spans cover the complete response and record a returned Task ID for
correlation. Task lookup/list/cancel operations
do not emit an `invoke_agent` span because they do not execute the agent.

The host emits one `SERVER` span for each valid A2A JSON-RPC operation using
the `Azure.AI.AgentServer.A2A` instrumentation scope. Span names are the A2A
method names (`SendMessage`, `GetTask`, and so on).
Attributes include Agent Card metadata and protocol, message, task, and `contextId`
identifiers supplied in the request. The host reuses Core's trace propagation,
exception recording, span completion, and non-blocking flush helpers. HTTP errors
and buffered unary JSON-RPC errors mark the span as failed, including JSON-RPC
errors transported with HTTP 200.

When the request has no Task ID, tracing also records the first Task ID returned
by a single-task operation. This lets a Task-ID search find its original
creation span.
`ListTasks` is not tagged with an arbitrary result Task ID.

Response-only context IDs and task states are not recorded.
Application metadata, prompts, and artifacts are not added to these spans.

These attributes follow the development-stage proposal in
[OpenTelemetry GenAI semantic conventions PR 195](https://github.com/open-telemetry/semantic-conventions-genai/pull/195)
and may evolve before that convention becomes stable.

The native `a2a-sdk` currently emits generic implementation-level spans in
addition to these semantic operation spans. To avoid duplicate server spans,
set this environment variable **before importing `a2a`**. The hosted invocation
span remains enabled:

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

To let the host construct the native handler and select default storage:

```python
host = A2AAgentServerHost(agent_card=card, agent_executor=executor)
host.run()
```

The package intentionally does not replace the native A2A SDK. Continue using
native A2A types for the agent card, executor, handler, task store, messages,
artifacts, and tasks.

### Task persistence

Executor-based construction follows the Activity host's storage-selection
pattern:

| Configuration | Task storage |
|---------------|--------------|
| Explicit `task_store` | The supplied native store, unchanged |
| Foundry-hosted, no explicit store | `FoundryTaskStore` backed by Core's generic state store |
| Local, no explicit store | Native `InMemoryTaskStore` |
| Existing `request_handler` | The handler and its storage are preserved; no replacement |

Supply exactly one of `agent_executor` and `request_handler`. When supplying
an existing handler, configure its storage directly instead of passing
`task_store` to the host.

`FoundryTaskStore` implements the native `save`, `get`, `list`, and `delete`
operations. It stores complete protobuf Task snapshots, including history and
artifacts. Lightweight listing metadata is saved atomically with each snapshot;
native filtering and pagination select the page before full snapshots are read.
Listing still scans key metadata to preserve native ordering and total counts,
but full history/artifact reads are limited to the requested page. Older preview
records without listing metadata require full reads until saved again.
Foundry enforces its configured caller-isolation scope on hosted item
operations using validated brokered context. Available platform-user, native
user, and tenant scopes are layered into storage keys. A raw user-ID header is not required when the request
has a brokered call ID; the opaque call ID is forwarded unchanged through Core,
never parsed or used as a durable owner key. Hosted requests without usable
identity or brokered context are rejected.

Every operation verifies that the actual backing-store descriptor enables
`user_isolation`, including reads of an existing store. A non-isolated or
unverifiable store is rejected; creation arguments are not treated as proof of
an existing store's configuration. Storage authorization failures are surfaced
rather than selecting an anonymous/shared partition.

The hosted default namespace uses the stable agent GUID (or agent name when a
GUID is unavailable), not the process or hosted-session ID. The host drains
its default native handler before shutdown callbacks and closes its default
store afterward. Explicit stores and existing handlers remain caller-owned.

To opt into persistence locally or choose a different named store:

```python
from azure.ai.agentserver.a2a import A2AAgentServerHost, FoundryTaskStore

store = FoundryTaskStore("my-agent/a2a-tasks")
host = A2AAgentServerHost(agent_card=card, agent_executor=executor, task_store=store)


@host.shutdown_handler
async def close_storage():
    await store.aclose()
```

Locally this uses Core's existing file-backed state store under
`AGENTSERVER_STATE_ROOT` (default `~/.agentserver`). Hosted operation uses the
Foundry storage service and its identity/permission requirements. Storage is
created lazily on the first save; reads do not create an empty store.
Storage failures are surfaced rather than falling back to hosted in-memory
storage. Store retention defaults to Core's 30 days and can be configured with
`item_ttl_seconds`. Large outputs should use artifact references where needed
to respect the state service's item-size limits.

**Persistence is not execution recovery:** saving a Task marked `WORKING` does
not restart its executor. This feature does not create Core resilient tasks
or checkpoint workflows. Those remain separate application choices.

Hosted persistence also requires the A2A gateway to deliver the platform
identity/brokered-context headers. A preview gateway may route native A2A
requests successfully while omitting this handoff. In that case the SDK rejects
storage access with a caller-context error; enabling the endpoint alone is not
proof that managed persistence is available. Do not disable isolation or supply
fabricated platform identity headers to work around a missing service handoff.

These APIs require the updated source or an alpha built after this feature;
previously published alpha wheels do not gain the new behavior automatically.
See [the persistence example](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-a2a/samples/04-state-store/README.md) for a restart test.

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

See the [sample setup and walkthroughs](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-a2a/samples)
for standalone and multi-protocol examples, a native local client,
and guidance on TaskStore durability and context reuse.

## Scope

This package hosts incoming A2A traffic. It does not provide an outbound A2A
client or intercept calls from the hosted agent to another agent.

The Foundry service rewrites the externally returned agent card. Container
security schemes, signatures, provider/branding fields, internal URLs, and
unsupported capabilities are not exposed to callers.

## Troubleshooting

- **Agent Card discovery returns 404:** check the server port and use
  `/a2a/.well-known/agent-card.json` for a local container. The public Foundry
  Agent Card route is different; local sample clients do not authenticate to
  that public endpoint.
- **A request returns `VERSION_NOT_SUPPORTED`:** use the native sample client,
  or explicitly send `A2A-Version: 1.0` with JSON-RPC requests.
- **Task lookup fails after restarting a sample:** the examples use
  `InMemoryTaskStore`. Its records do not survive a process restart. Reusing a
  context ID does not restore a lost Task or application history.

Core provides console logging for request failures and supports distributed
tracing through its configured exporters. See [distributed tracing](#distributed-tracing)
for the A2A span behavior. Do not include authorization headers or sensitive
message contents when sharing diagnostic logs.

## Next steps

- Follow the [sample setup and walkthroughs](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-a2a/samples)
  to discover an Agent Card, send a message, and retrieve a Task locally.
- Implement your agent with the native [A2A Python SDK](https://github.com/a2aproject/a2a-python)
  executor, request-handler, and TaskStore interfaces.
- Review the samples' state guidance before replacing in-memory storage, and
  use [multi-protocol composition](#host-a2a-and-invocations-together) when
  another Agent Server protocol must share the same process.

## Contributing

This project welcomes contributions and suggestions. Most contributions
require you to agree to a Contributor License Agreement (CLA) declaring that
you have the right to, and actually do, grant us the rights to use your
contribution. For details, visit [https://cla.microsoft.com](https://cla.microsoft.com).

This project has adopted the
[Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
