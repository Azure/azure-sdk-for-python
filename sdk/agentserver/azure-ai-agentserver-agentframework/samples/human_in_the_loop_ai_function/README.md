# Human-in-the-Loop Agent Framework Sample

This sample shows how to host a Microsoft Agent Framework agent inside Azure AI Agent Server while escalating responses to a real human when ai function requires approval. The sample is created by [agent-framework](https://github.com/microsoft/agent-framework/blob/main/python/samples/getting_started/tools/ai_function_with_approval_and_threads.py).

## Prerequisites

- Python 3.10+ and `pip`
- Azure CLI logged in with `az login` (used by `AzureCliCredential`)
- An Azure OpenAI chat deployment

### Environment configuration

Copy `.envtemplate` to `.env` and fill in your Azure OpenAI details:

```
AZURE_OPENAI_ENDPOINT=https://<endpoint-name>.cognitiveservices.azure.com/
OPENAI_API_VERSION=2025-03-01-preview
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=<deployment-name>
```

`main.py` automatically loads the `.env` file before spinning up the server.

## Run the hosted workflow agent

From this directory start the adapter host (defaults to `http://0.0.0.0:8088`):

```powershell
python main.py
```

## Send a user request

Send a `POST` request to `http://0.0.0.0:8088/responses`

```json
{
    "agent": {"name": "local_agent", "type": "agent_reference"},
    "stream": false,
    "input": "Add a dentist appointment on March 15th",
}
```

A response with human-review request looks like this (formatted for clarity):

```json
{
  "conversation": {"id": "<conversation_id>"},
  "output": [
    {...},
    {
      "type": "function_call",
      "id": "func_xxx",
      "name": "__hosted_agent_adapter_hitl__",
      "call_id": "<call_id>",
      "arguments": "{\"event_name\":\"Dentist Appointment\",\"date\":\"2024-03-15\"}"
    }
  ]
}
```

Capture three values from the response:

- `conversation.id`
- The `call_id` of the `__hosted_agent_adapter_hitl__` function call
- The `request_id` inside the serialized `agent_request`

## Provide human feedback

Respond by sending a `CreateResponse` request with `function_call_output` message that carries your review decision. Replace the placeholders before running the command:

```json
{
  "agent": {"name": "local_agent", "type": "agent_reference"},
  "stream": false,
  "convseration": {"id": "<conversation_id>"},
  "input": [
    {
      "call_id": "<call_id>",
      "output": "approve",
      "type": "function_call_output",
    }
  ]
}
```

Once the reviewer accepts the human feedback, the worker emits the approved assistant response and the HTTP call returns the final output.
