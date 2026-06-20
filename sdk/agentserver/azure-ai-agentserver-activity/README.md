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
- `apply_msal_patches()` — patches M365 SDK MSAL auth for Foundry containers (UserManagedIdentity with fmi_path)

## Examples

See the [samples directory](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/agentserver/azure-ai-agentserver-activity/samples) for runnable scenarios:

- `simple_activity_agent` — echo bot with welcome, invoke, installation events
- `streaming_activity_agent` — Azure OpenAI streaming via `context.streaming_response`
- `cards_activity_agent` — Adaptive Cards, Hero, Thumbnail, Receipt cards
- `auto_signin_activity_agent` — OAuth auto sign-in with Graph and GitHub
- `semantic_kernel_activity_agent` — Semantic Kernel agent with tools and multi-turn
- `suggested_actions_activity_agent` — quick-reply buttons

## Troubleshooting

### 403 Forbidden from Teams Developer Portal

When configuring blueprint backend, ensure you have the correct Azure authentication scope:

```bash
az login --scope https://dev.teams.microsoft.com/.default
```

If using `configure-blueprint-backend.ps1`, load environment variables from your `.azure` directory before running the script.

### Missing environment variables

Ensure all required azd environment variables are set before running scripts:

```bash
azd env get-values
```

## Next steps

- Review the [Azure AI Hosted Agent documentation](https://aka.ms/azsdk/foundry/hosted-agents)
- Explore the [Activity Protocol specification](https://aka.ms/azsdk/foundry/activity-protocol)
- Check the [`azure-ai-agentserver-core`](https://pypi.org/project/azure-ai-agentserver-core/) package for base host functionality
- Learn about deployment patterns in [Foundry quickstarts](https://aka.ms/azsdk/foundry/quickstarts)

## Contributing

This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit [https://cla.microsoft.com](https://cla.microsoft.com).

When you submit a pull request, a CLA bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.
