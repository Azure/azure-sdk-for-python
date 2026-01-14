pip install -e src/adapter/python
# Agent Framework Sample

This sample demonstrates how to use the agents hosting adapter with Microsoft Agent Framework.

## Prerequisites

> **Azure sign-in:** Run `az login` before starting the sample so `DefaultAzureCredential` can acquire a CLI token.

### Environment Variables

Copy `.envtemplate` to `.env` and supply:

```
AZURE_OPENAI_ENDPOINT=https://<endpoint-name>.cognitiveservices.azure.com/
OPENAI_API_VERSION=2025-03-01-preview
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=<deployment-name>
```

## Running the Sample

Follow these steps from this folder:

1) Start the agent server (defaults to 0.0.0.0:8088):

```bash
python main.py
```

2) Send a non-streaming request (returns a single JSON response):

```bash
curl -sS \
  -H "Content-Type: application/json" \
  -X POST http://localhost:8088/responses \
  -d "{\"input\":\"Add a dentist appointment on March 15th\",\"stream\":false}"
```

3) Send a streaming request (server-sent events). Use -N to disable curl buffering:

```bash
curl -N \
  -H "Content-Type: application/json" \
  -X POST http://localhost:8088/responses \
  -d "{\"input\":\"Add a dentist appointment on March 15th\",\"stream\":true}"
```
