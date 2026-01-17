# Chat Client With Foundry Tools

This sample demonstrates how to attach `FoundryToolsChatMiddleware` to an Agent Framework chat client so that:

- Foundry tools configured in your Azure AI Project are converted into Agent Framework `AIFunction` tools.
- The tools are injected automatically for each agent run.

## What this sample does

The script creates an Agent Framework agent using:

- `AzureOpenAIChatClient` for model inference
- `FoundryToolsChatMiddleware` to resolve and inject Foundry tools
- `from_agent_framework(agent).run()` to start an AgentServer-compatible HTTP server

## Prerequisites

- Python 3.10+
- An Azure AI Project endpoint
- A tool connection configured in that project (e.g. an MCP connection)
- Azure credentials available to `DefaultAzureCredential`

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Update `.env` in this folder with your values. At minimum you need:

```dotenv
AZURE_OPENAI_ENDPOINT=https://<your-azure-openai-resource>.openai.azure.com/
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=<deployment-name>
OPENAI_API_VERSION=<api-version>

AZURE_AI_PROJECT_ENDPOINT=https://<your-resource>.services.ai.azure.com/api/projects/<your-project>
AZURE_AI_PROJECT_TOOL_CONNECTION_ID=<your-tool-connection-id>
```

Notes:

- This sample uses `DefaultAzureCredential()`. Make sure you are signed in (e.g. `az login`) or otherwise configured.

## Run

```bash
python chat_client_with_foundry_tool.py
```

This starts a local Uvicorn server (it will keep running and wait for requests). If it looks "stuck" at startup, it may just be waiting for requests.

## Key code

The core pattern used by this sample:

```python
agent = AzureOpenAIChatClient(
    credential=DefaultAzureCredential(),
    middleware=FoundryToolsChatMiddleware(
        tools=[{"type": "mcp", "project_connection_id": tool_connection_id}],
    ),
).create_agent(
    name="FoundryToolAgent",
    instructions="You are a helpful assistant with access to various tools.",
)

from_agent_framework(agent).run()
```

## Troubleshooting

- **No tools found**: verify `AZURE_AI_PROJECT_TOOL_CONNECTION_ID` points at an existing tool connection in your project.
- **Auth failures**: confirm `DefaultAzureCredential` can acquire a token (try `az login`).
- **Import errors / weird agent_framework circular import**: ensure you are running the sample from this folder (not from inside the package module directory) so the external `agent_framework` dependency is imported correctly.

## Learn more

- Azure AI Agent Service: https://learn.microsoft.com/azure/ai-services/agents/
- Agent Framework: https://github.com/microsoft/agent-framework
