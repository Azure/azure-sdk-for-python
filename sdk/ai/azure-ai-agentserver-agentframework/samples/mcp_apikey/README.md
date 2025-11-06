pip install -e src/adapter/python
## Agent Framework MCP GitHub Token Sample

This sample mirrors the simpler `mcp_simple` Agent Framework sample but adds an MCP server (GitHub) that requires a Bearer token (`GITHUB_TOKEN`). The token is injected as an HTTP Authorization header when constructing the `MCPStreamableHTTPTool`.

### Script

- `mcp_apikey.py` – Creates a `ChatAgent` configured with an `AzureOpenAIChatClient` and a GitHub MCP tool, then serves it via the agents hosting adapter (`from_agent_framework(...).run_async()`).

## Prerequisites

> **Azure sign-in:** Run `az login` before starting the sample so `DefaultAzureCredential` can acquire a CLI token.

### Environment Variables

Copy `.envtemplate` to `.env` and supply:

```
AZURE_OPENAI_ENDPOINT=https://<endpoint-name>.cognitiveservices.azure.com/
OPENAI_API_VERSION=2025-03-01-preview
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=<deployment-name>
GITHUB_TOKEN=<your-github-token>
```

### GitHub Token Setup

To obtain a GitHub token for the MCP server:

1. Go to [GitHub Settings > Developer settings > Personal access tokens > Tokens (classic)](https://github.com/settings/tokens)
1. Click "Generate new token" → "Generate new token (classic)"
1. Select the minimum required scopes under the "repo" category. For this sample, the following scopes are sufficient:
   - `public_repo` (Access public repositories)
   - `repo:status` (Access commit statuses)
   If you need access to private repositories, also select `repo` (Full control of private repositories).
1. Click "Generate token"
1. Copy the token immediately (you won't be able to see it again)
1. Add it to your `.env` file as `GITHUB_TOKEN=<your-token>`

### Run

From this folder:

```bash
python mcp_apikey.py
```

### Test (non‑streaming example)

```bash
curl -X POST http://localhost:8088/responses \
  -H "Content-Type: application/json" \
  -d '{"input":"summarize the last change in <repo url>","stream":false}'
```

### Test (streaming example)

```bash
curl -X POST http://localhost:8088/responses \
  -H "Content-Type: application/json" \
  -d '{"input":"summarize the last change in <repo url>","stream":true}'
```
