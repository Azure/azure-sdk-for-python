# Agent Framework MCP Simple Python Sample

This sample demonstrates how to run a Microsoft Agent Framework `ChatAgent` that calls a Model Context Protocol (MCP) HTTP endpoint (Microsoft Learn MCP) using the Container Agents Adapter and the `AzureAIAgentClient` from the `agent-framework-azure-ai` package.

## What It Shows
- Creating an Agent Framework `ChatAgent` with an `AzureAIAgentClient`
- Adding an MCP tool via `MCPStreamableHTTPTool`
- Serving the agent over HTTP using the Container Agents Adapter (`from_agent_framework(...).run()`)
- Handling both streaming and non‑streaming response modes (client controlled via the `stream` flag in the request body)

## File Overview
- `mcp_simple.py` – Agent factory + server bootstrap. Loads `.env` relative to its location.
- `.env` – Local environment file with Azure AI project configuration variables.

## Prerequisites

> **Azure sign-in:** Run `az login` before starting the sample so `DefaultAzureCredential` can acquire a CLI token.

Packages actually imported by `simple-mcp.py`:
- agent-framework-azure-ai (published package with Agent Framework client + MCP support)
- agents_adapter
- azure-identity
- python-dotenv

Install from PyPI (from the repo root: `container_agents/`):
```bash
pip install agent-framework-azure-ai azure-identity python-dotenv

pip install -e src/adapter/python
```

Copy `.envtemplate` to `.env` and fill in real values:
```
AZURE_AI_PROJECT_ENDPOINT=<foundry-project-endpoint>
AZURE_AI_MODEL_DEPLOYMENT_NAME=<model-deployment-name>
AGENT_PROJECT_NAME=<agent-project-name-optional>
GITHUB_TOKEN=<your-github-token>
```
`AGENT_PROJECT_NAME` lets you override the Azure AI agent project used for the sample. If omitted, the SDK default is used.

## Running the Server
From this folder:

```bash
python simple-mcp.py
```

By default the adapter listens on `0.0.0.0:8088` (override with `DEFAULT_AD_PORT`).

## Making Requests
Non‑streaming:
```bash
curl -sS \
  -H "Content-Type: application/json" \
  -X POST http://localhost:8088/responses \
  -d "{\"input\":\"How do I create an Azure Storage Account using the Azure CLI?\",\"stream\":false}"
```

Streaming (Server‑Sent Events, keep `-N` to avoid curl buffering):
```bash
curl -sS \
  -H "Content-Type: application/json" \
  -X POST http://localhost:8088/responses  \
  -d "{\"input\":\"What is Microsoft Semantic Kernel in brief?\",\"stream\":true}"
```

## Sample Output
```
{
    "metadata": {},
    "agent": null,
    "conversation_id": null,
    "type": "message",
    "role": "assistant",
    "temperature": 1.0,
    "top_p": 1.0,
    "user": "",
    "id": "9adf0f68-6689-434d-98c4-be665c057bf5",
    "created_at": 1757651350,
    "output": [
        {
            "id": "b923901f-aefe-4ccf-ad01-6ce03cbc52dd",
            "status": "completed",
            "content": [
                {
                    "type": "output_text",
                    "text": "To create an Azure Storage Account using the Azure CLI, you can use the `az storage account create` command. Below is an example of the steps and command to create a new storage account:\n\n### Steps:\n1. **Ensure you are logged in** to Azure using the Azure CLI. If not, log in using:\n   ```\n   az login\n   ```\n\n2. **Select the appropriate subscription** if you have more than one:\n   ```\n   az account set --subscription <your-subscription-id>\n   ```\n\n3. **Create a resource group**, if you don’t already have one, using:\n   ```\n   az group create --name <resource-group-name> --location <region>\n   ```\n\n4. **Create the storage account** using:\n   ```\n   az storage account create \\\n     --name <storage-account-name> \\\n     --resource-group <resource-group-name> \\\n     --location <region> \\\n     --sku <sku> \\\n     --kind <kind>\n   ```\n\n### Command Parameters:\n- **`--name`**: Specifies the name of the storage account. The name must be globally unique and between 3 to 24 characters in length, using only alphanumeric characters.\n- **`--resource-group`**: The name of the resource group in which to create the storage account.\n- **`--location`**: The Azure region where the resource group and storage account will be created (e.g., `eastus`, `westus`, etc.).\n- **`--sku`**: Defines the performance tier of the storage account, such as `Standard_LRS`, `Standard_GRS`, `Standard_ZRS`, or `Premium_LRS`.\n- **`--kind`**: Specifies the storage account type, like `StorageV2` (recommended), `Storage`, or `BlobStorage`.\n\n### Example:\nCreate a general-purpose StorageV2 account in `East US` with `Standard_LRS` redundancy:\n```\naz group create --name myResourceGroup --location eastus\naz storage account create \\\n  --name mystorageaccount123 \\\n  --resource-group myResourceGroup \\\n  --location eastus \\\n  --sku Standard_LRS \\\n  --kind StorageV2\n```\n\n### Verifying the creation:\nOnce created, you can list your storage accounts in the resource group to verify:\n```\naz storage account list --resource-group <resource-group-name> --output table\n```\n\nThis command displays the storage account details in a table format.\n\nWould you like more help with defining any of the parameters?",
                    "annotations": []
                }
            ]
        }
    ],
    "parallel_tool_calls": true,
    "status": "completed",
    "object": "response"
}

```
```
event: response.created
data: {"type": "response.created", "sequence_number": 1, "response": {"metadata": {}, "temperature": 1.0, "top_p": 1.0, "user": "", "id": "41249d4a-f6e4-4a01-950b-b67e9c812a7b", "created_at": 1757651565, "output": [], "parallel_tool_calls": true, "status": "in_progress", "object": "response"}}

event: response.in_progress
data: {"type": "response.in_progress", "sequence_number": 2, "response": {"metadata": {}, "temperature": 1.0, "top_p": 1.0, "user": "", "id": "41249d4a-f6e4-4a01-950b-b67e9c812a7b", "created_at": 1757651565, "output": [], "parallel_tool_calls": true, "status": "in_progress", "object": "response"}}

event: response.output_item.added
data: {"type": "response.output_item.added", "sequence_number": 3, "output_index": 0, "item": {"type": "message", "role": "assistant", "id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "status": "in_progress", "content": []}}

event: response.content_part.added
data: {"type": "response.content_part.added", "sequence_number": 4, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "part": {"type": "output_text", "text": "", "annotations": []}}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 5, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": "Microsoft"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 6, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " Semantic"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 7, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " Kernel"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 8, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " ("}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 9, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": "SK"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 10, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": ")"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 11, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " is"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 12, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " an"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 13, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " open"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 14, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": "-source"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 15, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " software"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 16, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " development"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 17, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " kit"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 18, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " ("}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 19, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": "SDK"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 20, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": ")"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 21, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " designed"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 22, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " to"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 23, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " help"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 24, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " developers"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 25, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " build"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 26, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " AI"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 27, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " applications"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 28, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " by"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 29, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " seamlessly"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 30, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " integrating"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 31, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " large"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 32, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " language"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 33, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " models"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 34, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " ("}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 35, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": "LL"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 36, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": "Ms"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 37, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": "),"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 38, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " such"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 39, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " as"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 40, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " Open"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 41, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": "AI"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 42, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": "'s"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 43, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " GPT"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 44, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " or"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 45, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " Azure"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 46, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " Open"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 47, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": "AI"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 48, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " Service"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 49, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": ","}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 50, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " with"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 51, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " traditional"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 52, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " programming"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 53, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": "."}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 54, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " Semantic"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 55, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " Kernel"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 56, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " allows"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 57, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " developers"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 58, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " to"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 59, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " combine"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 60, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " natural"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 61, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " language"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 62, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " processing"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 63, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " capabilities"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 64, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " with"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 65, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " conventional"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 66, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " code"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 67, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " to"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 68, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " create"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 69, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " AI"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 70, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": "-based"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 71, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " solutions"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 72, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " that"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 73, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " include"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 74, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " memory"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 75, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " management"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 76, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": ","}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 77, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " complex"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 78, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " workflows"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 79, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": ","}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 80, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " embeddings"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 81, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": ","}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 82, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " and"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 83, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " intelligent"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 84, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " decision"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 85, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": "-making"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 86, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " features"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 87, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": "."}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 88, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " Its"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 89, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " extens"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 90, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": "ible"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 91, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " and"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 92, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " modular"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 93, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " design"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 94, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " supports"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 95, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " the"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 96, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " creation"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 97, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " of"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 98, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " complex"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 99, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": ","}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 100, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " mult"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 101, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": "iste"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 102, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": "p"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 103, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " pipelines"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 104, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " that"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 105, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " take"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 106, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " advantage"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 107, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " of"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 108, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " the"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 109, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " power"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 110, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " of"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 111, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " L"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 112, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": "LM"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 113, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": "s"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 114, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " while"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 115, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " allowing"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 116, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " fine"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 117, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": "-gr"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 118, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": "ained"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 119, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " control"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 120, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " for"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 121, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": " developers"}

event: response.output_text.delta
data: {"type": "response.output_text.delta", "sequence_number": 122, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "delta": "."}

event: response.output_text.done
data: {"type": "response.output_text.done", "sequence_number": 123, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "text": "Microsoft Semantic Kernel (SK) is an open-source software development kit (SDK) designed to help developers build AI applications by seamlessly integrating large language models (LLMs), such as OpenAI's GPT or Azure OpenAI Service, with traditional programming. Semantic Kernel allows developers to combine natural language processing capabilities with conventional code to create AI-based solutions that include memory management, complex workflows, embeddings, and intelligent decision-making features. Its extensible and modular design supports the creation of complex, multistep pipelines that take advantage of the power of LLMs while allowing fine-grained control for developers."}

event: response.content_part.done
data: {"type": "response.content_part.done", "sequence_number": 124, "item_id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "output_index": 0, "content_index": 0, "part": {"type": "output_text", "text": "Microsoft Semantic Kernel (SK) is an open-source software development kit (SDK) designed to help developers build AI applications by seamlessly integrating large language models (LLMs), such as OpenAI's GPT or Azure OpenAI Service, with traditional programming. Semantic Kernel allows developers to combine natural language processing capabilities with conventional code to create AI-based solutions that include memory management, complex workflows, embeddings, and intelligent decision-making features. Its extensible and modular design supports the creation of complex, multistep pipelines that take advantage of the power of LLMs while allowing fine-grained control for developers.", "annotations": []}}

event: response.output_item.done
data: {"type": "response.output_item.done", "sequence_number": 125, "output_index": 0, "item": {"type": "message", "role": "assistant", "id": "7c7115b0-b1b2-4682-9acd-5cb05a3c8123", "status": "completed", "content": [{"type": "output_text", "text": "Microsoft Semantic Kernel (SK) is an open-source software development kit (SDK) designed to help developers build AI applications by seamlessly integrating large language models (LLMs), such as OpenAI's GPT or Azure OpenAI Service, with traditional programming. Semantic Kernel allows developers to combine natural language processing capabilities with conventional code to create AI-based solutions that include memory management, complex workflows, embeddings, and intelligent decision-making features. Its extensible and modular design supports the creation of complex, multistep pipelines that take advantage of the power of LLMs while allowing fine-grained control for developers.", "annotations": []}]}}

event: response.completed
data: {"type": "response.completed", "sequence_number": 126, "response": {"metadata": {}, "temperature": 1.0, "top_p": 1.0, "user": "", "id": "41249d4a-f6e4-4a01-950b-b67e9c812a7b", "created_at": 1757651565, "output": [{"id": "08772107-2062-40ed-982e-704d685a84df", "type": "message", "role": "assistant", "status": "completed", "content": [{"type": "output_text", "text": "Microsoft Semantic Kernel (SK) is an open-source software development kit (SDK) designed to help developers build AI applications by seamlessly integrating large language models (LLMs), such as OpenAI's GPT or Azure OpenAI Service, with traditional programming. Semantic Kernel allows developers to combine natural language processing capabilities with conventional code to create AI-based solutions that include memory management, complex workflows, embeddings, and intelligent decision-making features. Its extensible and modular design supports the creation of complex, multistep pipelines that take advantage of the power of LLMs while allowing fine-grained control for developers.", "annotations": []}]}], "parallel_tool_calls": true, "status": "completed", "object": "response"}}
```

## Customization Ideas
- Add additional MCP tools (multiple `MCPStreamableHTTPTool` instances in a list)
- Combine MCP + local Python tool functions
- Swap `AzureChatClient` for a different model provider client supported by Agent Framework

## Troubleshooting
- 401/403 errors: Check Azure AI project endpoint & deployment values in `.env` and ensure your Azure login or service principal credentials are valid
- Name resolution / network errors: Verify the MCP endpoint URL is reachable (`curl https://learn.microsoft.com/api/mcp`)
- Empty / slow responses: Ensure the Azure AI deployment name matches an active model deployment in the project and that the service has sufficient quota

## Support
For Agent Framework issues: https://github.com/microsoft/agent-framework

For adapter issues, open an issue in this repository.
