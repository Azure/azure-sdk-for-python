# Human-in-the-Loop Agent Framework Sample

This sample shows how to host a Microsoft Agent Framework workflow inside Azure AI Agent Server while escalating responses to a real human when the reviewer executor decides that manual approval is required. The sample is provided by [agent-framework](https://github.com/microsoft/agent-framework/blob/main/python/samples/getting_started/workflows/agents/workflow_as_agent_human_in_the_loop.py).

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

For Human-in-the-loop scenario, the `HumanReviewRequest` and `ReviewResponse` are provided by user. User should provide functions for these classes that allow adapter convert the data to request payloads.

```py
@dataclass
class HumanReviewRequest:
    """A request message type for escalation to a human reviewer."""

    agent_request: ReviewRequest | None = None

    def convert_to_payload(self) -> str:  # called by adapter
        """Convert the HumanReviewRequest to a payload string."""
        request = self.agent_request
        payload: dict[str, Any] = {"agent_request": None}

        if request:
            payload["agent_request"] = {
                "request_id": request.request_id,
                "user_messages": [msg.to_dict() for msg in request.user_messages],
                "agent_messages": [msg.to_dict() for msg in request.agent_messages],
            }

        return json.dumps(payload)
```

```py
@dataclass
class ReviewResponse:
    """Structured response from Reviewer back to Worker."""

    request_id: str
    feedback: str
    approved: bool

    @staticmethod
    def convert_from_payload(payload: str) -> "ReviewResponse":
        """Convert a JSON payload string to a ReviewResponse instance."""
        data = json.loads(payload)
        return ReviewResponse(
            request_id=data["request_id"],
            feedback=data["feedback"],
            approved=data["approved"],
        )
```

From this directory start the adapter host (defaults to `http://0.0.0.0:8088`):

```powershell
python main.py
```

The worker executor produces answers, the reviewer executor always escalates to a person, and the adapter exposes the whole workflow through the `/responses` endpoint.



## Send a user request

Send a `POST` request to `http://0.0.0.0:8088/responses`

```json
{
    "agent": {"name": "local_agent", "type": "agent_reference"},
    "stream": false,
    "input": "Write code for parallel reading 1 million Files on disk and write to a sorted output file.",
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
      "arguments": "{\"agent_request\":{\"request_id\":\"<request_id>\",...}}"
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
      "output": "{\"request_id\":\"<request_id>\",\"approved\":true}",
      "type": "function_call_output",
    }
  ]
}
```

Once the reviewer accepts the human feedback, the worker emits the approved assistant response and the HTTP call returns the final output.
