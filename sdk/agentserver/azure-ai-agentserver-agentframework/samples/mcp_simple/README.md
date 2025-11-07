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
curl -sS \
# Agent Framework MCP Simple Python Sample

This sample demonstrates how to run a Microsoft Agent Framework `ChatAgent` that calls a Model Context Protocol (MCP) HTTP endpoint (Microsoft Learn MCP) using the agentserver adapter and the `AzureOpenAIChatClient` from the `agent-framework` package.

## What It Shows

- Creating an Agent Framework `ChatAgent` with an `AzureOpenAIChatClient`
- Adding an MCP tool via `MCPStreamableHTTPTool`
- Serving the agent over HTTP using the agentserver adapter (`from_agent_framework(...).run()`)
- Handling both streaming and non‑streaming response modes (client controlled via the `stream` flag in the request body)

## File Overview

- `mcp_simple.py` – Agent factory + server bootstrap. Loads `.env` relative to its location.
- `.env` – Local environment file with Azure AI project configuration variables.

## Prerequisites

> **Azure sign-in:** Run `az login` before starting the sample so `DefaultAzureCredential` can acquire a CLI token.

### Install Dependencies

Initialize a virtual environment and then install dependencies:

```bash
pip install -r ./requirements.txt --pre
```

### Environment Variables

Copy `.envtemplate` to `.env` and supply:

```
AZURE_OPENAI_ENDPOINT=https://<endpoint-name>.cognitiveservices.azure.com/
OPENAI_API_VERSION=2025-03-01-preview
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=<deployment-name>
```

## Running the Server

From this folder:

```bash
python mcp_simple.py
```

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

[comment]: # ( cspell:ignore mult ained )

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
