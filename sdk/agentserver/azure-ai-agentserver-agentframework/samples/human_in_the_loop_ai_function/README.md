# Human-in-the-Loop Agent Framework Sample

This sample demonstrates how to host a Microsoft Agent Framework agent inside Azure AI Agent Server and escalate function-call responses to a human reviewer whenever approval is required. It is adapted from the [agent-framework sample](https://github.com/microsoft/agent-framework/blob/main/python/samples/getting_started/tools/ai_function_with_approval_and_threads.py).

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

## Thread persistence

The sample uses `JsonLocalFileAgentThreadRepository` for `AgentThread` persistence, creating a JSON file per conversation ID under the sample directory. An in-memory alternative, `InMemoryAgentThreadRepository`, lives in the `azure.ai.agentserver.agentframework.persistence` module.

To store thread messages elsewhere, inherit from `SerializedAgentThreadRepository` and override the following methods:

- `read_from_storage(self, conversation_id: str) -> Optional[Any]`
- `write_to_storage(self, conversation_id: str, serialized_thread: Any)`

These hooks let you plug in any backing store (blob storage, databases, etc.) without changing the rest of the sample.

## Run the hosted agent

From this directory start the adapter host (defaults to `http://0.0.0.0:8088`):

```powershell
python main.py
```

## Send a user request

Send a `POST` request to `http://0.0.0.0:8088/responses`:

```json
{
    "agent": {"name": "local_agent", "type": "agent_reference"},
    "stream": false,
    "input": "Add a dentist appointment on March 15th",
}
```

A response that requires a human decision looks like this (formatted for clarity):

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

Capture these values from the response; you will need them to provide feedback:

- `conversation.id`
- The `call_id` associated with `__hosted_agent_adapter_hitl__`

## Provide human feedback

Send a `CreateResponse` request with a `function_call_output` message that contains your decision (`approve`, `reject`, or additional guidance). Replace the placeholders before running the command:

```json
{
  "agent": {"name": "local_agent", "type": "agent_reference"},
  "stream": false,
  "conversation": {"id": "<conversation_id>"},
  "input": [
    {
      "call_id": "<call_id>",
      "output": "approve",
      "type": "function_call_output",
    }
  ]
}
```

When the reviewer response is accepted, the worker emits the approved assistant response and the HTTP call returns the final output.
