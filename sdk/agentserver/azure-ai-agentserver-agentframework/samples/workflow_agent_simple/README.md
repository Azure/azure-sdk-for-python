## Workflow Agent Simple Sample (Python)

This sample hosts a two-step Agent Framework workflow—`Writer` followed by `Reviewer`—through the Azure AI Agent Server Adapter. The writer creates content, the reviewer provides the final response, and the adapter exposes the workflow through the same HTTP surface as any hosted agent.

### What `workflow_agent_simple.py` does
- Builds a workflow with `WorkflowBuilder`
- Passes a workflow factory (`lambda: create_workflow(client)`) to `from_agent_framework(...).run_async()`, so a fresh workflow is created per request.
- Uses `Agent(client=AzureOpenAIResponsesClient(project_endpoint=..., credential=...))` for the writer and reviewer nodes.

The workflow factory is invoked for each incoming request, so keep workflow construction deterministic and side-effect free.

---

## Prerequisites
- Python 3.10+
- Azure CLI authenticated with `az login` (required for `AzureCliCredential`).
- An Azure AI project that already hosts a chat model deployment supported by the Agent Framework Azure client.

---

## Setup
1. Copy `.envtemplate` to `.env` and fill in your project details:
     ```
     AZURE_AI_PROJECT_ENDPOINT=<foundry-project-endpoint>
     AZURE_AI_MODEL_DEPLOYMENT_NAME=<model-deployment-name>
     ```
2. Install the sample dependencies:
     ```bash
     pip install -r requirements.txt
     ```

---

## Run the Workflow Agent
From this folder:

```bash
python workflow_agent_simple.py
```

The adapter starts the server on `http://0.0.0.0:8088` by default.

---

## Send Requests
- **Non-streaming:**
    ```bash
    curl -sS \
        -H "Content-Type: application/json" \
        -X POST http://localhost:8088/runs \
        -d '{"input":"Create a slogan for a new electric SUV that is affordable and fun to drive","stream":false}'
    ```

---

## Related Resources
- Agent Framework repo: https://github.com/microsoft/agent-framework
- Adapter package docs: `azure.ai.agentserver.agentframework` in this SDK

---

## License & Support
This sample follows the repository LICENSE. For questions about the Agent Framework itself, open an issue in the Agent Framework GitHub repository.
