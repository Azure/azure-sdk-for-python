# Simple LangGraph Agent with Foundry Managed Checkpointer

This sample hosts a LangGraph ReAct-style agent and uses `FoundryCheckpointSaver` to persist
checkpoints in Azure AI Foundry managed storage.

With Foundry managed checkpoints, graph state is stored remotely so conversations can resume across
requests and server restarts without self-managed storage.

### What `main.py` does

- Creates an `AzureChatOpenAI` model and two tools (`get_word_length`, `calculator`)
- Builds a LangGraph agent with `create_react_agent(..., checkpointer=saver)`
- Creates `FoundryCheckpointSaver(project_endpoint, credential)` and runs the server via
  `from_langgraph(...).run_async()`

---

## Prerequisites

- Python 3.10+
- Azure CLI authenticated with `az login` (required for `AzureCliCredential`)
- An Azure AI Foundry project endpoint
- An Azure OpenAI chat deployment (for example `gpt-4o`)

---

## Setup

1. Create a `.env` file in this folder:
   ```env
   AZURE_AI_PROJECT_ENDPOINT=https://<resource>.services.ai.azure.com/api/projects/<project-id>
   AZURE_OPENAI_ENDPOINT=https://<resource>.openai.azure.com/
   AZURE_OPENAI_API_KEY=<api-key>
   OPENAI_API_VERSION=2025-03-01-preview
   AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=gpt-4o
   ```

2. Install dependencies:
   ```bash
   pip install azure-ai-agentserver-langgraph python-dotenv azure-identity langgraph
   ```

---

## Run the Agent

From this folder:

```bash
python main.py
```

The adapter starts the server on `http://0.0.0.0:8088` by default.

---

## Send Requests

Non-streaming example:

```bash
curl -sS \
  -H "Content-Type: application/json" \
  -X POST http://localhost:8088/responses \
  -d '{
    "agent": {"name": "local_agent", "type": "agent_reference"},
    "stream": false,
    "input": "What is (15 * 4) + 6?",
    "conversation": {"id": "test-conversation-1"}
  }'
```

Use the same `conversation.id` on follow-up requests to continue the checkpointed conversation state.

---

## Related Resources

- LangGraph docs: https://langchain-ai.github.io/langgraph/
- Adapter package docs: `azure.ai.agentserver.langgraph` in this SDK
