# LangGraph MCP Simple Sample

This sample shows how to wrap a LangGraph ReAct-style agent that is augmented with MCP (Model Context Protocol) tools (sourced from Microsoft Learn) and expose it through the Azure AI Agents Adapter so it can be called using the standard responses endpoint.

## What It Does

`mcp_simple.py`:
1. Loads environment variables from a local `.env` file (see template below).
2. Creates an Azure OpenAI chat model (`gpt-4o`) via `AzureChatOpenAI`.
3. Constructs an MCP multi-server client (`MultiServerMCPClient`) pointing at the Microsoft Learn MCP endpoint.
4. Fetches available MCP tools and builds a LangGraph ReAct agent with those tools (`create_react_agent`).
5. Hosts the agent using `from_langgraph(...).run_async()` so it is available over HTTP on `http://localhost:8088` (default adapter port).

## Folder Contents

- `mcp_simple.py` – Main script that builds and serves the agent.
- `.env-template` – Template for required Azure OpenAI environment variables.
- `.env` – (User created) Actual secrets/endpoint values. Not committed.

## Prerequisites

Dependencies used by `mcp_simple.py`:
- agents_adapter with langgraph extra (brings langgraph, langchain, langchain-openai)
- python-dotenv
- langchain-mcp-adapters

Install (from repo root):
```bash
pip install -e container_agents_adapter/python[langgraph]
pip install python-dotenv langchain-mcp-adapters
```

Environment needs Azure OpenAI variables (see below). Requires Python 3.11+.

## Environment Variables

Copy `.env-template` to `.env` and fill in real values:
```
AZURE_OPENAI_API_KEY=<api-key>
AZURE_OPENAI_ENDPOINT=https://<endpoint-name>.cognitiveservices.azure.com/
OPENAI_API_VERSION=2025-03-01-preview
```
If you use a deployment name different from `gpt-4o`, adjust the `model="gpt-4o"` parameter in `mcp_simple.py` accordingly (e.g., the model argument must match your Azure OpenAI deployment name, not the base model family if they differ).

## (Dependencies Covered Above)

## Run the Sample

From the `mcp_simple` folder (or anywhere after install) run:
```bash
python mcp_simple.py
```
The adapter will start an HTTP server (default: `http://localhost:8088`). When ready, you can send a request to the unified responses endpoint.

## Test the Agent

Non-streaming example:
```bash
curl -X POST http://localhost:8088/responses \
  -H "Content-Type: application/json" \
  -d '{
    "agent": {"name": "local_agent", "type": "agent_reference"},
    "stream": false,
    "input": "Give me a short summary about Azure OpenAI"
  }'
```

Streaming example (server will stream delta events):
```bash
curl -N -X POST http://localhost:8088/responses \
  -H "Content-Type: application/json" \
  -d '{
    "agent": {"name": "local_agent", "type": "agent_reference"},
    "stream": true,
    "input": "List two learning resources about Azure Functions"
  }'
```

Alternatively, you can send the richer structured message format:
```bash
curl -X POST http://localhost:8088/responses \
  -H "Content-Type: application/json" \
  -d '{
    "agent": {"name": "local_agent", "type": "agent_reference"},
    "stream": false,
    "input": [{
      "type": "message",
      "role": "user",
      "content": [{"type": "input_text", "text": "What learning paths cover Azure AI?"}]
    }]
  }'
```

## MCP Tooling Notes

- `MultiServerMCPClient` connects to one or more MCP servers; here we configure a single `mslearn` server.
- `get_tools()` returns tool schemas that LangGraph incorporates, enabling the agent to decide when to call MCP tools.
- The Microsoft Learn MCP endpoint can surface search / retrieval style tools (subject to availability) so the agent can ground answers.

## Customization Ideas

- Add more MCP endpoints by extending the dictionary passed to `MultiServerMCPClient`.
- Swap `create_react_agent` for a custom LangGraph graph if you need more control (e.g., tool prioritization, guardrails, memory).
- Introduce logging or tracing (e.g., LangSmith) by configuring callbacks on the model or agent.

## Troubleshooting

| Issue | Likely Cause | Fix |
|-------|--------------|-----|
| 401 / auth errors from model | Wrong or missing key / endpoint | Re-check `.env` values and Azure OpenAI resource permissions |
| Model not found | Deployment name mismatch | Use your actual Azure deployment name in `AzureChatOpenAI(model=...)` |
| No tools available | MCP endpoint change / network issue | Confirm the MCP URL and that it returns tool definitions |
| Import errors for langgraph or adapter | Extras not installed | Re-run `pip install -e .[langgraph]` |


## Related Samples

See `samples/langgraph/agent_calculator` for another LangGraph + adapter example with arithmetic tools.

---
Happy hacking! Modify and extend the MCP tool set to build richer contextual agents.
