# Azure AI Agent Server Activity client library for Python

The `azure-ai-agentserver-activity` package provides the Foundry container integration host for Activity Protocol traffic in Azure AI Hosted Agent containers. It plugs into [`azure-ai-agentserver-core`](https://pypi.org/project/azure-ai-agentserver-core/) and exposes a protocol endpoint with Foundry-required header, tracing, and error behavior.

## Getting started

### Install the package

```bash
pip install azure-ai-agentserver-activity
```

### Prerequisites

- Python 3.10 or later

## Key concepts

### ActivityAgentServerHost

`ActivityAgentServerHost` is an `AgentServerHost` subclass for Activity Protocol traffic. It provides:

- `POST /activity/messages` (and the `POST /api/messages` alias) for inbound activities.

### Usage patterns

**Build the M365 stack (default)** — register handlers on the host's `agent_app`:

```python
from azure.ai.agentserver.activity import ActivityAgentServerHost

app = ActivityAgentServerHost()

@app.agent_app.activity("message")
async def on_message(context, state):
    await context.send_activity(f"Echo: {context.activity.text}")

@app.agent_app.error
async def on_error(context, error):
    await context.send_activity(f"Error: {error}")

app.run()
```

**Build the M365 stack, with overrides** — same default path, but override any
components you want to control (the host builds the rest from the environment):

```python
from microsoft_agents.hosting.core import MemoryStorage
from azure.ai.agentserver.activity import ActivityAgentServerHost

# Override just the storage backend; connection manager / adapter / authorization
# / config are still built for you. Add digital_worker=True for the blueprint model.
app = ActivityAgentServerHost(storage=MemoryStorage())
```

**Foundry durable storage** — drop-in durable state for the M365 bridge, backed by
Foundry-managed Activity state storage instead of the in-memory default:

```python
from azure.ai.agentserver.activity import ActivityAgentServerHost, FoundryStorage

storage = FoundryStorage()
app = ActivityAgentServerHost(storage=storage)
```

**Inject a pre-built `AgentApplication`** — host an M365 `AgentApplication` you built yourself:

```python
from azure.ai.agentserver.activity import ActivityAgentServerHost

# agent_app: a fully-built microsoft_agents AgentApplication (with an adapter)
app = ActivityAgentServerHost.from_agent_application(agent_app)
app.run()
```

**Custom handler** — you own the request pipeline (the M365 SDK is not initialized):

```python
from starlette.responses import Response

from azure.ai.agentserver.activity import ActivityAgentServerHost

async def handle(request):
    activity = request.state.activity  # parsed dict
    # Custom processing...
    return Response(status_code=202)

app = ActivityAgentServerHost.from_request_handler(handle)
app.run()
```

### Request header contract

`POST /activity/messages` consumes:

- `x-agent-session-id` (preferred session source)
- `x-agent-conversation-id`
- `x-agent-user-id` (per-user identity) and `x-agent-foundry-call-id` (per-request call ID, container protocol `2.0.0`)
- `traceparent`, `tracestate`, and `baggage`

### Public API

- `ActivityAgentServerHost` — the host class. Constructed directly, it builds the
  M365 stack and acts as the underlying M365 `AgentApplication`: register handlers
  and reach the full M365 surface (`activity`/`error`/`message`/`proactive`/`auth`
  ...) directly on the host. Optional keyword overrides: `digital_worker`,
  `storage`, `connection_manager`, `adapter`, `authorization`, `config`.
- `ActivityAgentServerHost.from_agent_application(agent_app)` — host a pre-built
  M365 `AgentApplication` (the adapter is taken from `agent_app.adapter`).
- `ActivityAgentServerHost.from_request_handler(handler)` — host a custom async
  request handler; the M365 SDK is not initialized.
- `get_hosted_agent_env(*, digital_worker=False)` — return a config mapping
  (`os.environ` overlaid with the derived `CONNECTIONS__*` settings from the
  Foundry-native `FOUNDRY_AGENT_*` env) **without mutating the environment**. The
  default constructor derives this for you; call it yourself only when you build
  the `MsalConnectionManager` (or a pre-built `AgentApplication`) manually — see
  the `03-self-hosted-app` sample.
- `ActivityAgentServerHost.adapter` — the channel adapter for the underlying
  `AgentApplication`.
- `FoundryStorage` — platform-managed durable storage for M365 conversation, user,
  and proactive state. Implements the M365 Agents SDK `Storage` interface. Each
  M365 storage key is already a scope identifier (for example
  `f"{channel_id}/conversations/{conversation_id}"` or
  `f"{channel_id}/users/{user_id}"`), so `FoundryStorage` backs each one with its
  own lazily-created `azure.ai.agentserver.core.storage.FoundryStateStore`
  ("store name = scope" — no shared namespace); user-shaped keys automatically
  get `user_isolation=True` (override via `is_user_scoped=`).

## Examples

See the [samples directory](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-activity/samples) for runnable scenarios, ordered as a learning path:

- `01-echo` — the simplest agent: the host builds the M365 stack and you register handlers directly on it to echo the user's message back.
- `02-custom-components` — override one or more M365 components (storage, connection manager, adapter, authorization, config) while the host builds the rest.
- `03-self-hosted-app` — build the M365 `AgentApplication` yourself and host it with `from_agent_application`.
- `04-custom-handler` — own the request pipeline with `from_request_handler` (the M365 SDK is not initialized).
- `05-multi-protocol` — compose the Activity and Invocations protocols on a single server.
- `06-foundry-storage-state` — durable conversation and user state with `FoundryStorage`.
- `07-foundry-storage-proactive` — durable proactive conversation references with `FoundryStorage`.
- `08-foundry-storage-history` — persist the full conversation transcript with `FoundryStorage` (`/history` and `/clear` commands).

## Troubleshooting

### `ImportError`: M365 Agents SDK not installed

Constructing `ActivityAgentServerHost()` directly (or via `from_agent_application`)
requires the M365 Agents SDK. Install it:

```bash
pip install microsoft-agents-hosting-core microsoft-agents-authentication-msal microsoft-agents-activity azure-identity
```

Alternatively, use `ActivityAgentServerHost.from_request_handler(...)`, which does
not initialize the M365 SDK.

### `TypeError`: handler must be an async function

`from_request_handler(...)` requires an `async def` handler
(`async def handle(request) -> Response`). A plain `def` is rejected.

### `AttributeError` when accessing `agent_app`

`app.agent_app` (and handler registration via `@app.agent_app.activity(...)` /
`@app.agent_app.error`) is only available when the host builds or is given an M365
`AgentApplication` (the default constructor or `from_agent_application`). A host
created with `from_request_handler(...)` does not expose the M365 surface.

## Next steps

- Review the [Azure AI Hosted Agent documentation](https://aka.ms/azsdk/foundry/hosted-agents)
- Explore the [Activity Protocol specification](https://aka.ms/azsdk/foundry/activity-protocol)
- Check the [`azure-ai-agentserver-core`](https://pypi.org/project/azure-ai-agentserver-core/) package for base host functionality
- Learn about deployment patterns in [Foundry quickstarts](https://aka.ms/azsdk/foundry/quickstarts)

## Contributing

This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit [https://cla.microsoft.com](https://cla.microsoft.com).

When you submit a pull request, a CLA bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.
