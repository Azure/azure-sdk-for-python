# Workflow Agent with Foundry Managed Checkpoints

This sample hosts a two-step Agent Framework workflow—`Writer` followed by `Reviewer`—and uses
`FoundryCheckpointRepository` to persist workflow checkpoints in Azure AI Foundry managed storage.

With Foundry managed checkpoints, workflow state is stored remotely so long-running conversations can
resume even after the host process restarts, without managing your own storage backend.

### What `main.py` does

- Builds a workflow with `WorkflowBuilder` (writer + reviewer)
- Creates a `FoundryCheckpointRepository` pointed at your Azure AI Foundry project
- Passes both to `from_agent_framework(..., checkpoint_repository=...)` so the adapter spins up an
  HTTP server (defaults to `0.0.0.0:8088`)

---

## Prerequisites

- Python 3.10+
- Azure CLI authenticated with `az login` (required for `AzureCliCredential`)
- An Azure AI Foundry project with a chat model deployment

---

## Setup

1. Create a `.env` file in this folder:
   ```
   AZURE_AI_PROJECT_ENDPOINT=https://<resource>.services.ai.azure.com/api/projects/<project-id>
   AZURE_AI_MODEL_DEPLOYMENT_NAME=<model-deployment-name>
   ```

2. Install dependencies:
   ```bash
   pip install azure-ai-agentserver-agentframework agent-framework-azure-ai azure-identity python-dotenv
   ```

---

## Run the Workflow Agent

From this folder:

```bash
python main.py
```

The adapter starts the server on `http://0.0.0.0:8088` by default.

---

## Send Requests

**Non-streaming:**

```bash
curl -sS \
    -H "Content-Type: application/json" \
    -X POST http://localhost:8088/responses \
    -d '{
      "agent": {"name": "local_agent", "type": "agent_reference"},
      "stream": false,
      "input": "Write a short blog post about cloud-native AI applications",
      "conversation": {"id": "test-conversation-1"}
    }'
```

The `conversation.id` ties requests to the same checkpoint session. Subsequent requests with the same
ID will resume the workflow from its last checkpoint.

---

## Checkpoint Repository Options

The `checkpoint_repository` parameter in `from_agent_framework` accepts any `CheckpointRepository` implementation:

| Repository | Use case |
|---|---|
| `InMemoryCheckpointRepository()` | Quick demos; checkpoints vanish when the process exits |
| `FileCheckpointRepository("<path>")` | Local file-based persistence |
| `FoundryCheckpointRepository(project_endpoint, credential)` | Azure AI Foundry managed remote storage (this sample) |

---

## Related Resources

- Agent Framework repo: https://github.com/microsoft/agent-framework
- Adapter package docs: `azure.ai.agentserver.agentframework` in this SDK
