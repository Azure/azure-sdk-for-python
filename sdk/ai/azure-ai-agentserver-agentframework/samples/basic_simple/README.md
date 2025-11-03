# Agent Framework Simple Python Sample

This sample demonstrates how to use the Container Agents Adapter with Microsoft Agent Framework to create a simple weather agent in python.

## Prerequisites

Only the packages actually imported by `minimal_example.py`:

> **Azure sign-in:** Run `az login` before starting the sample so `DefaultAzureCredential` can acquire a CLI token.

Required:
- agent-framework-azure-ai (published package containing the Agent Framework Python client)
- azure-identity (provides `DefaultAzureCredential`)
- python-dotenv (loads `.env` for local development)
- agents_adapter (this repo)

Install from PyPI (no local wheel bundle necessary):
```bash
pip install agent-framework-azure-ai azure-identity python-dotenv

pip install -e src/adapter/python
```

### Environment Variables
Copy `.envtemplate` to `.env` and supply:
```
AZURE_AI_PROJECT_ENDPOINT=https://<account>.services.ai.azure.com/api/projects/<project-name>
AZURE_AI_MODEL_DEPLOYMENT_NAME=<model-deployment-name>
```

Optional (improves diagnostics but not required to run the sample):
- `AGENT_PROJECT_NAME` — the Azure AI Project resource ID (e.g., `/subscriptions/<sub>/resourceGroups/<rg>/providers/Microsoft.MachineLearningServices/workspaces/<workspace>`)

Notes:
- `python-dotenv` is used to load the `.env` file at startup for local development convenience.
- The command above installs every required Agent Framework component; no extra subpackage installs are necessary.

### Agent Framework Project Information

- Repository: https://github.com/microsoft/agent-framework/tree/main/python
- Team: Microsoft Agent Framework Team

## Dependencies

Core runtime packages used by `minimal_example.py`:

- `agent-framework-azure-ai` (provides `AzureAIAgentClient` and Azure AI helpers)
- `agents_adapter` (this repo; provides `from_agent_framework` and the HTTP adapter)
- `azure-identity` (for `DefaultAzureCredential`)
- `python-dotenv` (loads `.env` when running locally)

> These are already satisfied if you ran the `pip install agent-framework-azure-ai azure-identity python-dotenv` command above, but they're listed explicitly here for clarity.

## Additional Requirements

You'll also need to install the agents adapter and its dependencies (covered in the command above when run from repo root). If you prefer to install separately:

```bash
pip install -e src/adapter/python
```

## Configuration

1. Azure AI Project Configuration: Update your `.env` with the Azure AI Project endpoint and model deployment name that should power this agent.
2. Azure Authentication: The sample uses `DefaultAzureCredential` for authentication. Ensure you're logged in to Azure CLI (`az login`) or have appropriate service principal environment variables set before running the sample.

## Running the Sample

Follow these steps from this folder:

1) Start the agent server (defaults to 0.0.0.0:8088):

```bash
python minimal_example.py
```

2) Send a non‑streaming request (returns a single JSON response):

```bash
curl -sS \
  -H "Content-Type: application/json" \
  -X POST http://localhost:8088/responses \
  -d "{\"input\":\"What's the weather like in Seattle?\",\"stream\":false}"
```

Sample output (non‑streaming):

```
{
  "metadata": {},
  "temperature": 1.0,
  "top_p": 1.0,
  "user": "",
  "id": "8f1c6295-1ea9-4394-80b9-b13079606a48",
  "created_at": "2025-08-26T17:19:45.188692+00:00",
  "output": [
    {
      "id": "5e31d5b8-2511-43f4-9922-d7184bb8fb08",
      "status": "completed",
      "content": [
        {
          "type": "output_text",
          "text": "The weather in Seattle is stormy with a high of 16\u00b0C. Stay safe and dry!",
          "annotations": []
        }
      ]
    }
  ],
  "instructions": "",
  "parallel_tool_calls": true,
  "status": "completed",
  "object": "response"
}
```

3) Send a streaming request (server-sent events). Use -N to disable curl buffering:

```bash
curl -N \
  -H "Content-Type: application/json" \
  -X POST http://localhost:8088/responses \
  -d "{\"input\":\"What's the weather like in New York?\",\"stream\":true}"
```

Sample output (streaming):

```
data: {"type": "response.function_call_arguments.delta", "sequence_number": 1, "item_id": "0e5a646d-8dda-401c-a11e-d9d5adeb6090", "output_index": 0, "delta": ""}
data: {"type": "response.function_call_arguments.delta", "sequence_number": 1, "item_id": "5c34fc9a-fba5-4061-b4b2-f079dec4790e", "output_index": 0, "delta": "{"}
data: {"type": "response.function_call_arguments.delta", "sequence_number": 1, "item_id": "8dcb87dd-2ebb-40c0-b98d-951ceba85c13", "output_index": 0, "delta": "location"}
data: {"type": "response.function_call_arguments.delta", "sequence_number": 1, "item_id": "1562cbf2-d0ca-4480-b1e1-1d1533d89141", "output_index": 0, "delta": "\":\""}
data: {"type": "response.function_call_arguments.delta", "sequence_number": 1, "item_id": "7505363d-d81e-4aee-89ba-1f8f9c614f2d", "output_index": 0, "delta": "New"}
data: {"type": "response.function_call_arguments.delta", "sequence_number": 1, "item_id": "9c65b53e-22ae-4f50-9b17-f0675adec507", "output_index": 0, "delta": " York"}
data: {"type": "response.function_call_arguments.delta", "sequence_number": 1, "item_id": "8e2f7aa5-ab5b-4b98-910d-ed6d302871ec", "output_index": 0, "delta": "\"}"}
data: {"type": "response.output_text.delta", "sequence_number": 1, "item_id": "5a1d2da4-10e9-4004-acbf-8e0fa528c77f", "output_index": 0, "content_index": 0, "delta": "The"}
data: {"type": "response.output_text.delta", "sequence_number": 1, "item_id": "d9720fc0-b3d9-446c-886b-38ff279fe659", "output_index": 0, "content_index": 0, "delta": " weather"}
data: {"type": "response.output_text.delta", "sequence_number": 1, "item_id": "89e4fa7a-4883-4d08-a2bd-a11945d0b2f9", "output_index": 0, "content_index": 0, "delta": " in"}
data: {"type": "response.output_text.delta", "sequence_number": 1, "item_id": "0be2fa62-0a38-40e4-8108-61d38cdea559", "output_index": 0, "content_index": 0, "delta": " New"}
data: {"type": "response.output_text.delta", "sequence_number": 1, "item_id": "e69172a8-2cf8-442c-b8d3-7de6c0353e72", "output_index": 0, "content_index": 0, "delta": " York"}
data: {"type": "response.output_text.delta", "sequence_number": 1, "item_id": "ca2bd5b2-72ff-44ea-b0d3-8bc09966fac3", "output_index": 0, "content_index": 0, "delta": " is"}
data: {"type": "response.output_text.delta", "sequence_number": 1, "item_id": "6625e071-cb41-4df9-8eb2-52d070798ec5", "output_index": 0, "content_index": 0, "delta": " currently"}
data: {"type": "response.output_text.delta", "sequence_number": 1, "item_id": "8e9faf62-c912-4b66-af9f-46e4b48aaee3", "output_index": 0, "content_index": 0, "delta": " cloudy"}
data: {"type": "response.output_text.delta", "sequence_number": 1, "item_id": "3d727933-1d3f-4e25-8204-91828c0cec54", "output_index": 0, "content_index": 0, "delta": " with"}
data: {"type": "response.output_text.delta", "sequence_number": 1, "item_id": "91959f36-8ed5-4162-9c90-0d5735136c62", "output_index": 0, "content_index": 0, "delta": " a"}
data: {"type": "response.output_text.delta", "sequence_number": 1, "item_id": "45ea3d75-b592-4adc-823f-fa8b63512ee3", "output_index": 0, "content_index": 0, "delta": " high"}
data: {"type": "response.output_text.delta", "sequence_number": 1, "item_id": "f0018154-3d3c-4dd3-b466-a3bf91eb7f73", "output_index": 0, "content_index": 0, "delta": " of"}
data: {"type": "response.output_text.delta", "sequence_number": 1, "item_id": "41f27c4f-0507-44a2-a58a-b527134d81da", "output_index": 0, "content_index": 0, "delta": " "}
data: {"type": "response.output_text.delta", "sequence_number": 1, "item_id": "2feff464-6618-4398-b126-576a4e1366b2", "output_index": 0, "content_index": 0, "delta": "22"}
data: {"type": "response.output_text.delta", "sequence_number": 1, "item_id": "998b4b05-10dc-4d1a-92ef-26a30afd27e7", "output_index": 0, "content_index": 0, "delta": "\u00b0C"}
data: {"type": "response.output_text.delta", "sequence_number": 1, "item_id": "788a51d4-88d9-4098-802c-2473502d84e9", "output_index": 0, "content_index": 0, "delta": "."}
```

Notes
- The server port can be changed by setting `DEFAULT_AD_PORT` in the environment before starting the server.
- Ensure your `.env` contains valid `AZURE_AI_PROJECT_ENDPOINT` and `AZURE_AI_MODEL_DEPLOYMENT_NAME` values and that Azure authentication via `DefaultAzureCredential` works (e.g., run `az login` or set service principal env vars) before invoking the endpoints.

Also can run this file `./try_agent_framework_adapter.py` to understand the agent framework adapter.


## Sample Code Overview

The `minimal_example.py` demonstrates:
- Creating a simple weather tool function
- Initializing an Azure AI Agent with `AzureAIAgentClient`
- Using the Container Agents Adapter to run the agent
- Streaming responses through the adapter endpoints backed by Azure AI

## Support

For issues specific to the Agent Framework package, please refer to:
- Agent Framework Repository: https://github.com/microsoft/agent-framework/tree/main/python
- Contact the Microsoft Agent Framework team for release timeline questions