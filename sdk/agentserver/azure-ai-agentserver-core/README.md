# Azure AI Agent Server Core client library for Python

The `azure-ai-agentserver-core` package provides the foundation host framework for building Azure AI Hosted Agent containers. It handles the protocol-agnostic infrastructure — health probes, graceful shutdown, OpenTelemetry tracing, and ASGI serving — so that protocol packages can focus on their endpoint logic.

## Memory snapshot task initialization

The draft integration separates task definitions from session-bound TaskManager
initialization. Resilient tasks must still be explicitly enabled.

`FOUNDRY_MEMORY_SNAPSHOT_ENABLED=true` defers enabled tasks in the temporary
capture sandbox until the platform after-restore hook. After session hydration,
the manager is prepared before the application callback, and automatic recovery
follows that callback. An absent value or `false` activates requested tasks during
ordinary cold/local startup. For standalone Core and Invocations,
`set_resilient_tasks_enabled(False)` keeps task execution disabled on both paths.
Responses independently requests its runtime through `resilient_background` or
`steerable_conversations`; the Invocations switch does not disable those options.
Present values must be literal `true` or `false` (case-insensitive). The variable
does not gate running tasks or lease renewal after activation.

Task startup checkpoints completed phases by restore ID and owns the manager
through shutdown, including managers created after lifespan startup. Existing
best-effort recovery dispatches reclaimed work immediately during the hook.
FHA admits new requests after successful restore.

Submit startup tasks from the existing `after_restore_handler` after rebuilding
dependencies. Capture-time submissions are not queued or replayed; no additional
session-start callback or launch-intent registry is included. Local tests are
not proof of hosted golden restoration. See the [design specification](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-core/docs/memory-snapshot-task-integration.md)
for lifecycle ordering, launcher compatibility requirements, validation, and
the selected startup-submission flow.

## Getting started

### Install the package

```bash
pip install azure-ai-agentserver-core
```

OpenTelemetry tracing with Azure Monitor and OTLP exporters is included by default.

### Prerequisites

- Python 3.10 or later

## Key concepts

### AgentServerHost

`AgentServerHost` is the host process for Azure AI Hosted Agent containers. It provides:

- **Health probe** — `GET /readiness` returns `200 OK` when the server is ready.
- **Snapshot lifecycle** — Private platform hooks prepare a process for capture and restore session-specific state.
- **Graceful shutdown** — On `SIGTERM` the server drains in-flight requests (default 30 s timeout) before exiting.
- **OpenTelemetry tracing** — Automatic span creation with Azure Monitor and OTLP export when configured.
- **Hypercorn ASGI server** — Serves on `0.0.0.0:${PORT:-8088}` with HTTP/1.1.

Protocol packages (e.g. `azure-ai-agentserver-invocations`) subclass `AgentServerHost` and add their endpoints in `__init__`.

### Environment variables

| Variable | Description | Default |
|---|---|---|
| `PORT` | Listen port | `8088` |
| `FOUNDRY_AGENT_NAME` | Agent name (used in tracing) | `""` |
| `FOUNDRY_AGENT_VERSION` | Agent version (used in tracing) | `""` |
| `FOUNDRY_PROJECT_ENDPOINT` | Azure AI Foundry project endpoint | `""` |
| `FOUNDRY_PROJECT_ARM_ID` | Foundry project ARM resource ID (used in tracing) | `""` |
| `FOUNDRY_AGENT_SESSION_ID` | Default session ID when not provided per-request | `""` |
| `APPLICATIONINSIGHTS_CONNECTION_STRING` | Azure Monitor connection string | — |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OTLP collector endpoint | — |

## Examples

`AgentServerHost` is typically used via a protocol package. The simplest setup with the invocations protocol:

```python
from azure.ai.agentserver.invocations import InvocationAgentServerHost
from starlette.responses import JSONResponse

app = InvocationAgentServerHost()

@app.invoke_handler
async def handle(request):
    body = await request.json()
    return JSONResponse({"greeting": f"Hello, {body['name']}!"})

app.run()
```

### Per-request identity (multi-user sessions)

On container protocol `2.0.0` a single agent session can serve **multiple users**. Each request carries `x-agent-user-id` (the user — partition state by it) and an opaque `x-agent-foundry-call-id` (the per-request caller identity). Read both via `get_request_context()`; the SDK forwards **only** the call ID on outbound Foundry calls — `x-agent-user-id` is never echoed. Forwarding the call ID lets a tool server resolve which user made the request and act on their behalf.

```python
import os

import httpx
from azure.ai.agentserver.core import get_request_context


def foundry_headers() -> dict[str, str]:
    # Echoes x-agent-foundry-call-id only; x-agent-user-id is never forwarded.
    return dict(get_request_context().platform_headers())


async def call_toolbox(query: str) -> str:
    user_id = get_request_context().user_id  # for the container's OWN per-user state
    # Attach the call ID PER CALL — a toolbox MCP session is long-lived and serves many
    # users/turns, so never bake one call's ID into the client's static headers.
    async with httpx.AsyncClient() as mcp:
        resp = await mcp.post(
            f"{os.environ['FOUNDRY_PROJECT_ENDPOINT']}/toolboxes/github/mcp",
            headers={"Authorization": f"Bearer {get_agent_token()}", **foundry_headers()},
            json={"jsonrpc": "2.0", "method": "tools/call",
                  "params": {"name": "list_my_assigned_issues", "arguments": {}}},
        )
    return resp.text  # the toolbox resolved the caller from the call ID and acted as that user
```

### Draft original-subject model attribution

`get_request_context().original_subject` carries a separate immutable snapshot
of the proposed original-subject `oid`, `tid`, and `idtype` fields. Responses,
Invocations (HTTP, streaming, and WebSocket), and native Activity consume the
same metadata. The existing user-state identifier and `platform_headers()`
behavior are unchanged.

This is a draft contract for owner review, not an enabled budget feature.
The proposed single header is an RFC 9651 Structured Fields dictionary:

```text
x-ms-original-subject: oid="<object-id>", tid="<tenant-id>", idtype="user"
```

This draft accepts only `oid`, `tid`, and `idtype` string members, in any
order, without parameters. Strings use Structured Fields quoting and escaping,
not JSON or positional CSV. Duplicate header fields or keys, unknown keys,
malformed syntax, and non-string values raise `ValueError`. Missing keys are
omitted, not encoded as spaces or literal `"null"`. A missing header means no
subject; an empty string member remains distinct from a missing member.
The retired three-header draft is not consumed as a fallback.

For a supported model endpoint whose owner has enabled the contract, pass
`get_request_context().model_attribution_headers()` as **per-call** headers
(for example, `extra_headers` on a model SDK call). Keep the model's existing
credential. Never put a user's tuple in shared client defaults or send it to
external/BYO endpoints, arbitrary URLs, tools, or storage callbacks.

```python
from azure.ai.agentserver.core import get_request_context

response = await model_client.responses.create(
    model=model_deployment,
    input="Hello",
    extra_headers=get_request_context().model_attribution_headers(),
)
```

The helper supplies the correctly quoted dictionary value and the current call
ID when available. Do not `json.dumps` the original-subject value: that is a
different wire format. Other independently supported per-call headers can be
merged into this mapping without changing their own encoding.

No model client is patched automatically. Absent metadata returns an empty
mapping; partial, empty, or HTTP-unsafe metadata raises `ValueError` rather
than silently forwarding an incomplete tuple. Non-user and unknown
classifications are preserved for receiver-side policy, not treated as users.
Header assertions are not identity proof: receiver provenance validation,
invocation binding, wire names, and missing-metadata policy still require
owner agreement. Durable restore and detached execution are not supported by
this draft. It does not change authentication, billing, or enforcement.

### Subclassing AgentServerHost

For custom protocol implementations, subclass `AgentServerHost` and add routes:

```python
from azure.ai.agentserver.core import AgentServerHost
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

class MyAgentHost(AgentServerHost):
    def __init__(self, **kwargs):
        my_routes = [Route("/my-endpoint", self._handle, methods=["POST"])]
        existing = list(kwargs.pop("routes", None) or [])
        super().__init__(routes=existing + my_routes, **kwargs)

    async def _handle(self, request: Request):
        return JSONResponse({"status": "ok"})

app = MyAgentHost()
app.run()
```

### Readiness handler

By default, `GET /readiness` returns `200 OK` with
`{"status": "healthy"}`. Register a readiness handler to replace the default
response with application-specific readiness logic:

```python
from azure.ai.agentserver.core import AgentServerHost
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

app = AgentServerHost()

@app.readiness_handler
async def readiness(request: Request) -> Response:
    if await dependencies_ready():
        return JSONResponse({"status": "healthy"})

    return JSONResponse({"status": "not_ready"}, status_code=503)
```

When no handler is registered, the built-in healthy response remains
unchanged.

### Shutdown handler

Register a cleanup function that runs during graceful shutdown:

```python
app = AgentServerHost()

@app.shutdown_handler
async def on_shutdown():
    # Close database connections, flush buffers, etc.
    pass
```

### Memory snapshot lifecycle handlers

The host always registers the private platform routes
`POST /_agent/before-snapshot` and `POST /_agent/after-restore`, with equivalent
aliases at `POST /_before_snapshot` and `POST /_after_restore`. All four routes
are processed by the framework, including restore validation and environment
and configuration hydration. Registering application handlers is optional;
when absent, only the application callbacks are skipped. Use the hooks to
release connections that must not be copied into a memory snapshot and rebuild
them for the restored session:

```python
from azure.ai.agentserver.core import AgentServerHost, AgentSessionContext

app = AgentServerHost()

@app.before_snapshot_handler
async def before_snapshot():
    await database.close()

@app.after_restore_handler
async def after_restore(context: AgentSessionContext):
    # context.session_env_overrides has already been applied to os.environ.
    await database.connect()
```

Lifecycle calls are serialized and idempotent. A repeated `after-restore`
request with the same `restore_id` does not invoke the handler again, while a
new `restore_id` for the same session starts a new restore cycle. The server
rejects attempts to reuse a restored process for a different session.

When the host's protocols request task execution, the SDK prepares a session-bound
TaskManager before the application `after_restore_handler`. Invocations uses
`set_resilient_tasks_enabled(True)`; Responses independently uses
`resilient_background=True` or `steerable_conversations=True`. Rebuild dependencies first,
then submit `@task`/`@multi_turn_task` work using the normal task APIs:

```python
@app.after_restore_handler
async def after_restore(context: AgentSessionContext):
    await database.connect()
    await startup_work.start(input={"session_id": context.session_id})
```

Here `startup_work` is an application's decorated task method. Automatic initial
recovery and the periodic scanner start after the handler returns; HTTP 200 waits
for that initialization, not for background work to finish. `.run()` is also
available for bounded work, but awaiting long-running completion can exceed the
restore timeout. A failed hook can be retried: reconcile unfinished task IDs and
persist completion state if startup must run only once per logical session.
Request routes retain their own protocol's opt-out even on a mixed host. The
restore handler uses the owning host's runtime if any protocol requests one.
The Invocations switch does not disable an enabled Responses option, and
ordinary cold startup does not invoke the restore handler.

Protocol-specific hosts can override the protected `_before_snapshot` and
`_after_restore` methods to extend the lifecycle before application callbacks
run. The host still performs validation, session environment and configuration
hydration, serialization, rollback, and idempotency, so subclass extensions
cannot accidentally omit those required steps. Overrides should call the
corresponding `super()` method first so multiple protocol layers compose
cooperatively:

```python
class ProtocolAgentHost(AgentServerHost):
    async def _after_restore(self, context: AgentSessionContext):
        await super()._after_restore(context)
        await self._rebuild_protocol_state(context)
```

### Durable state storage

`FoundryStateStore` is a durable, server-backed key-value store for agent state
— session memory, per-user preferences, counters, and checkpoints — bound to
one explicit, caller-named store, with single-item optimistic concurrency,
tag-filtered key listing, and store-level TTL.

```python
from azure.ai.agentserver.core.storage import FoundryStateStore

# Endpoint and credential resolve from FOUNDRY_PROJECT_ENDPOINT + DefaultAzureCredential.
# get_or_create() resolves (or creates, on first use) the store in one call.
store = await FoundryStateStore.get_or_create("checkpoints/thread-abc", user_isolation=True)
async with store:
    await store.set_item("step-1", {"done": False})
    item = await store.get_item("step-1")
    print(item.value)  # {"done": False}
```

> The default credential path uses `DefaultAzureCredential`, which requires the
> optional `azure-identity` package (`pip install azure-identity`). Alternatively,
> pass any `azure.core.credentials_async.AsyncTokenCredential` explicitly to
> `get_or_create()` and `azure-identity` is not needed.

Reads return typed `StateStoreItem` values; writes return typed item metadata and use
single-item `If-Match` concurrency. Session/conversation scoping is expressed in
the store name itself, and item expiry is controlled by the store's
`item_ttl_seconds` setting. See the [Durable State Store Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-core/docs/state-store-guide.md)
for the full API, the store lifecycle, and common gotchas, and
[state_store_sample.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-core/samples/state_store_sample.py)
for a runnable end-to-end example.


### Configuring tracing

The default observability setup stamps every OpenTelemetry span and log record
with a `microsoft.foundry = "True"` attribute, including telemetry from
protocol packages and underlying frameworks. Conflicting values for this
attribute are overridden; the existing `gen_ai.provider.name` attribute is
left untouched. Custom observability callbacks that replace the default setup
are responsible for configuring their own enrichment.

Tracing is enabled automatically when an Application Insights connection string is available:

```python
app = AgentServerHost(
    applicationinsights_connection_string="InstrumentationKey=...",
)
```

Or via environment variable:

```bash
export APPLICATIONINSIGHTS_CONNECTION_STRING="InstrumentationKey=..."
python my_agent.py
```

Azure Monitor uses 100% trace sampling by default. Standard OpenTelemetry
sampling configuration through `OTEL_TRACES_SAMPLER` and
`OTEL_TRACES_SAMPLER_ARG` takes precedence when explicitly set. This controls
sampling only; exporter queues, process termination, and transport or ingestion
failures can still prevent trace delivery.

Azure SDK, HTTPX, Requests, urllib, and urllib3 instrumentation are disabled by
default to avoid automatically tracing every outbound HTTP request. To enable
selected instrumentations, configure the host's observability callback:

```python
from functools import partial

from azure.ai.agentserver.core import AgentServerHost, configure_observability

app = AgentServerHost(
    configure_observability=partial(
        configure_observability,
        instrumentation_options={
            "azure_sdk": {"enabled": True},
            "httpx": {"enabled": True},
            "requests": {"enabled": True},
        },
    )
)
```

OTLP export is enabled when `OTEL_EXPORTER_OTLP_ENDPOINT` is set. HTTP/protobuf
is the default protocol. To use an OTLP/gRPC collector, install the optional
gRPC extra and set `OTEL_EXPORTER_OTLP_PROTOCOL=grpc`:

```bash
pip install "azure-ai-agentserver-core[otlp-grpc]"
export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4317"
export OTEL_EXPORTER_OTLP_PROTOCOL="grpc"
python my_agent.py
```

### Resilient long-running agents

The `@task` decorator builds crash-resilient agents that survive container restarts, OOM kills, and redeployments. Task state is persisted to a task store, enabling automatic recovery and multi-turn suspend/resume patterns.

The resilient task subsystem is **opt-in**: call `set_resilient_tasks_enabled(True)` (before host startup, typically at import time) so the framework constructs the `TaskManager` and runs crash recovery. Without it, `.run()` / `.start()` raise `TaskManagerNotInitialized`.

```python
from azure.ai.agentserver.core.tasks import (
    set_resilient_tasks_enabled,
    task,
    TaskContext,
)

# Opt in to the durable task subsystem (required for @task to run).
set_resilient_tasks_enabled(True)

@task(name="process_document")
async def process_document(ctx: TaskContext[dict]) -> dict:
    # ctx.entry_mode is "fresh" | "resumed" | "recovered".
    # The framework re-invokes the handler from the top after a
    # crash; ctx.input survives, so the handler picks up.
    summary = await analyze(ctx.input["document_url"])
    return {"summary": summary}

result = await process_document.run(
    task_id="doc-42", input={"document_url": "..."},
)
print(result)  # {"summary": "..."}
```
See the [Developer Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-core/docs/tasks-guide.md) for streaming, multi-turn suspend/resume, retries, timeouts, steering, and the patterns reference.
See the [Developer Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-core/docs/tasks-guide.md) for streaming, multi-turn suspend/resume, retries, timeouts, steering, and the patterns reference.

## Troubleshooting

### Logging

Set the log level to `DEBUG` for detailed diagnostics:

```python
app = AgentServerHost(log_level="DEBUG")
```

### Reporting issues

To report an issue with the client library, or request additional features, please open a GitHub issue [here](https://github.com/Azure/azure-sdk-for-python/issues).

## Next steps

- Install [`azure-ai-agentserver-invocations`](https://pypi.org/project/azure-ai-agentserver-invocations/) to add the invocation protocol endpoints.
- Read the [Resilient Task Developer Guide](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/agentserver/azure-ai-agentserver-core/docs/tasks-guide.md) for crash-resilient long-running agents.
- See the [container image spec](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver) for the full hosted agent contract.

## Contributing

This project welcomes contributions and suggestions. Most contributions require
you to agree to a Contributor License Agreement (CLA) declaring that you have
the right to, and actually do, grant us the rights to use your contribution.
For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether
you need to provide a CLA and decorate the PR appropriately (e.g., label,
comment). Simply follow the instructions provided by the bot. You will only
need to do this once across all repos using our CLA.

This project has adopted the
[Microsoft Open Source Code of Conduct][code_of_conduct]. For more information,
see the Code of Conduct FAQ or contact opencode@microsoft.com with any
additional questions or comments.

[code_of_conduct]: https://opensource.microsoft.com/codeofconduct/
