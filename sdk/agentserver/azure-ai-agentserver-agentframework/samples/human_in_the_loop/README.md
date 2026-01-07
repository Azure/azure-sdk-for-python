# Human-in-the-Loop Agent Framework Sample

This sample shows how to host a Microsoft Agent Framework workflow inside Azure AI Agent Server while escalating responses to a real human when the reviewer executor decides that manual approval is required.

## Prerequisites

- Python 3.10+ and `pip`
- Azure CLI logged in with `az login` (used by `AzureCliCredential`)
- An Azure OpenAI chat deployment

### Environment configuration

1. Copy `.envtemplate` to `.env` and fill in your Azure OpenAI details:

   ```
   AZURE_OPENAI_ENDPOINT=https://<endpoint-name>.cognitiveservices.azure.com/
   OPENAI_API_VERSION=2025-03-01-preview
   AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=<deployment-name>
   ```

2. Create a virtual environment (optional but recommended) and install the sample dependencies:

   ```powershell
   python -m venv .venv
   . .venv/Scripts/Activate.ps1
   pip install -r requirements.txt
   ```

`main.py` automatically loads the `.env` file before spinning up the server.

## Run the workflow-hosted agent

From this directory start the adapter host (defaults to `http://0.0.0.0:8088`):

```powershell
python main.py
```

The worker executor produces answers, the reviewer executor always escalates to a person, and the adapter exposes the whole workflow through the `/responses` endpoint.

For Human-in-the-loop scenario, the `HumanReviewRequest` and `ReviewResponse` are classes provided by user. User should provide functions for these classes that allow adapter convert the data to request payloads.


## Send a user request

Save the following payload to `request.json` (adjust the prompt as needed):

```json
{
  "input": "Plan a 2-day Seattle trip that balances food and museums.",
  "stream": false
}
```

Then call the server (PowerShell example):

```pwsh
$body = Get-Content .\request.json -Raw
Invoke-RestMethod -Uri http://localhost:8088/responses -Method Post -ContentType "application/json" -Body $body `
  | ConvertTo-Json -Depth 8
```

A human-review interrupt looks like this (formatted for clarity):

```json
{
  "conversation": {"id": "conv_xxx"},
  "output": [
    {
      "type": "function_call",
      "name": "__hosted_agent_adapter_hitl__",
      "call_id": "call_xxx",
      "arguments": "{\"agent_request\":{\"request_id\":\"req_xxx\",...}}"
    }
  ]
}
```

Capture three values from the response:

- `conversation.id`
- The `call_id` of the `__hosted_agent_adapter_hitl__` function call
- The `request_id` inside the serialized `agent_request`

## Provide human feedback

Respond by sending a `function_call_output` message that carries your review decision. Replace the placeholders before running the command:

```pwsh
$payload = @{
  stream = $false
  conversation = @{ id = "<conversation-id>" }
  input = @(
    @{
      type = "function_call_output"
      call_id = "<call_id>"
      output = '{"request_id":"<request-id>","feedback":"Approved","approved":true}'
    }
  )
} | ConvertTo-Json -Depth 5

Invoke-RestMethod -Uri http://localhost:8088/responses -Method Post -ContentType "application/json" -Body $payload `
  | ConvertTo-Json -Depth 8
```

Update the JSON string in `output` to reject a response:

```json
{"request_id":"<request-id>","feedback":"Missing safety disclaimers.","approved":false}
```

Once the reviewer accepts the human feedback, the worker emits the approved assistant response and the HTTP call returns the final output.
