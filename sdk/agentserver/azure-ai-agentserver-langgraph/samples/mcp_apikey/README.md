# LangGraph MCP GitHub Token Sample

This sample shows how to wrap a LangGraph ReAct-style agent that is augmented with an MCP (Model Context Protocol) server requiring an API key / personal access token (GitHub) and expose it through the Azure AI Agents Adapter so it can be called via the unified `responses` endpoint.

Compared to `mcp_simple`, this version demonstrates adding authorization headers (Bearer token) for an MCP server (GitHub) that expects a token.

## What It Does

`mcp_apikey.py`:
1. Loads environment variables from a local `.env` file.
2. Creates an Azure OpenAI chat model deployment (defaults to `gpt-4o`, override with `AZURE_OPENAI_DEPLOYMENT`).
3. Reads a GitHub access token (`GITHUB_TOKEN`). This can be a classic or fine‑grained PAT (or an OAuth access token you obtained elsewhere).
4. Constructs a `MultiServerMCPClient` pointing at the public GitHub MCP endpoint and injects the token as an `Authorization: Bearer ...` header.
5. Fetches the available MCP tools exposed by the GitHub server.
6. Builds a LangGraph ReAct agent (`create_react_agent`) with those tools.
7. Hosts the agent using `from_langgraph(...).run_async()` making it available over HTTP (default: `http://localhost:8088`).

## Folder Contents

- `mcp_apikey.py` – Main script that builds and serves the token-authenticated MCP agent.
- `.env-template` – Template for required environment variables.
- `.env` – (User created) Actual secrets/endpoint values. Not committed.

## Prerequisites

Dependencies used by `mcp_apikey.py`:
- agents_adapter[langgraph]
- python-dotenv
- langchain-mcp-adapters

Install:
```bash
pip install -e container_agents_adapter/python[langgraph]
pip install python-dotenv langchain-mcp-adapters
```

Requires Python 3.11+, Azure OpenAI deployment, and a `GITHUB_TOKEN`.

## Environment Variables

Copy `.env-template` to `.env` and fill in values:
```
AZURE_OPENAI_API_KEY=<azure-openai-key>
AZURE_OPENAI_ENDPOINT=https://<endpoint-name>.cognitiveservices.azure.com/
OPENAI_API_VERSION=2025-03-01-preview
# Optional if your deployment name differs from gpt-4o
AZURE_OPENAI_DEPLOYMENT=<your-deployment-name>

# GitHub MCP auth (required)
GITHUB_TOKEN=<your-github-token>
```
Notes:
- `AZURE_OPENAI_DEPLOYMENT` defaults to `gpt-4o` if omitted.
- Do NOT commit `.env`.

## (Dependencies Covered Above)

## Run the Sample

From the `mcp-apikey` folder (or anywhere after install) run:
```bash
python mcp_apikey.py
```
The adapter starts an HTTP server (default `http://localhost:8088`).

## Test the Agent

Non-streaming example:
```bash
curl -X POST http://localhost:8088/responses \
  -H "Content-Type: application/json" \
  -d '{
    "agent": {"name": "local_agent", "type": "agent_reference"},
    "stream": false,
    "input": "Use ONLY the Microsoft Learn MCP tools exposed by the connected MCP server (no built-in web search, no cached data).call the \"list tools\" capability and record the exact tool names returned.Use the search tool to query: \"Model Context Protocol\" (limit 3).Pick the top result and use the fetch tool to retrieve details/content for that document."
  }'
```

Streaming example (server will stream delta events):
```bash
curl -N -X POST http://localhost:8088/responses \
  -H "Content-Type: application/json" \
  -d '{
    "agent": {"name": "local_agent", "type": "agent_reference"},
    "stream": true,
    "input": "Use ONLY the Microsoft Learn MCP tools exposed by the connected MCP server (no built-in web search, no cached data).call the \"list tools\" capability and record the exact tool names returned.Use the search tool to query: \"Model Context Protocol\" (limit 3).Pick the top result and use the fetch tool to retrieve details/content for that document."
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
      "content": [{"type": "input_text", "text": "Use ONLY the Microsoft Learn MCP tools exposed by the connected MCP server (no built-in web search, no cached data).call the \"list tools\" capability and record the exact tool names returned.Use the search tool to query: \"Model Context Protocol\" (limit 3).Pick the top result and use the fetch tool to retrieve details/content for that document."}]
    }]
  }'
```

## Customization Ideas

- Add additional MCP endpoints (e.g., documentation, search, custom internal tools).
- Swap `create_react_agent` for a custom LangGraph graph with memory, guardrails, or ranking.
- Integrate tracing / telemetry (LangSmith, OpenTelemetry) by adding callbacks to the model / agent.

## Troubleshooting

| Issue | Likely Cause | Fix |
|-------|--------------|-----|
| 401 from MCP server | Missing/invalid `GITHUB_TOKEN` | Regenerate PAT; ensure env var loaded |
| 401 / auth from model | Azure key/endpoint incorrect | Re-check `.env` values |
| Model not found | Deployment name mismatch | Set `AZURE_OPENAI_DEPLOYMENT` correctly |
| No tools listed | GitHub MCP endpoint changed | Verify endpoint URL & token scopes |
| Import errors | Extras not installed | Re-run dependency install |

## Related Samples

See `samples/langgraph/mcp_simple` for a no-auth MCP example and `samples/langgraph/agent_calculator` for arithmetic tooling.

---
Extend this pattern to securely integrate additional authenticated MCP servers.
