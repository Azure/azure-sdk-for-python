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

- `POST /activity/messages` for inbound activities.

### Usage patterns

**Decorator-based (recommended)** — zero SDK wiring:

```python
from azure.ai.agentserver.activity import ActivityAgentServerHost

app = ActivityAgentServerHost()

@app.activity("message")
async def on_message(context, state):
    await context.send_activity(f"Echo: {context.activity.text}")

@app.error
async def on_error(context, error):
    await context.send_activity(f"Error: {error}")

app.run()
```

**Foundry durable storage** — drop-in durable state for the M365 bridge:

```python
from azure.ai.agentserver.activity import ActivityAgentServerHost, FoundryStorage

storage = FoundryStorage()
app = ActivityAgentServerHost(storage=storage)
```

**Custom handler** — full control over the M365 SDK pipeline:

```python
from azure.ai.agentserver.activity import ActivityAgentServerHost

async def handle(request):
    activity = request.state.activity  # parsed dict
    # Custom processing...
    return Response(status_code=202)

app = ActivityAgentServerHost(handler=handle)
app.run()
```

### Request header contract

`POST /activity/messages` consumes:

- `x-agent-session-id` (preferred session source)
- `x-agent-conversation-id`
- `x-agent-user-isolation-key` and `x-agent-chat-isolation-key`
- `traceparent`, `tracestate`, and `baggage`

### Public API

- `ActivityAgentServerHost` — the host class
- `FoundryStorage` — platform-managed durable storage for M365 conversation, user, and proactive state
- `apply_msal_patches()` — patches M365 SDK MSAL auth for Foundry containers (UserManagedIdentity with fmi_path)

## Samples

See [samples/README.md](samples/README.md) for runnable scenarios:

- `simple_activity_agent` — echo bot with welcome, invoke, installation events
- `streaming_activity_agent` — Azure OpenAI streaming via `context.streaming_response`
- `cards_activity_agent` — Adaptive Cards, Hero, Thumbnail, Receipt cards
- `auto_signin_activity_agent` — OAuth auto sign-in with Graph and GitHub
- `semantic_kernel_activity_agent` — Semantic Kernel agent with tools and multi-turn
- `suggested_actions_activity_agent` — quick-reply buttons
- `foundry_storage_state_agent` — durable conversation and user state with `FoundryStorage`
- `foundry_storage_proactive_agent` — durable proactive conversation references with `FoundryStorage`
