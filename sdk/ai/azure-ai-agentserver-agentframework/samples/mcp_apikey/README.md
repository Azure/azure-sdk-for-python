## Agent Framework MCP GitHub Token Sample

This sample mirrors the simpler `mcp_simple` Agent Framework sample but adds an MCP server (GitHub) that requires a Bearer token (`GITHUB_TOKEN`). The token is injected as an HTTP Authorization header when constructing the `MCPStreamableHTTPTool`.

### Script
- `mcp_apikey.py` – Defines `create_agent()` returning a `ChatAgent` configured with an `AzureAIAgentClient` and a GitHub MCP tool, then serves it via the Azure AI Agents Adapter (`from_agent_framework(...).run()`).

## Prerequisites

> **Azure sign-in:** Run `az login` before starting the sample so `DefaultAzureCredential` can acquire a CLI token.

Imports in `mcp_apikey.py` require:
- agent-framework-azure-ai (published package with Agent Framework client and MCP tooling)
- agents_adapter
- azure-identity
- python-dotenv

Install from PyPI:
```bash
pip install agent-framework-azure-ai azure-identity python-dotenv

pip install -e src/adapter/python
```

### Environment Variables
Copy `.envtemplate` to `.env` and supply:
```
AZURE_AI_PROJECT_ENDPOINT=https://<account>.services.ai.azure.com/api/projects/<project-name>
AZURE_AI_MODEL_DEPLOYMENT_NAME=<model-deployment-name>
GITHUB_TOKEN=<your-github-token>
```

Optional:
- `AGENT_PROJECT_NAME` — Azure AI Project resource ID used for telemetry metadata.

### Run
From this folder:
```bash
python mcp_apikey.py
```
Server listens on `0.0.0.0:8088` by default (override with `DEFAULT_AD_PORT`).

### Test (non‑streaming example)
```bash
curl -X POST http://localhost:8088/responses \
  -H "Content-Type: application/json" \
  -d '{"input":"use github tool to get latest commit in <repo_name> repo from github, the repo owner is <repo-owner-name>. And please use json format in response and should include mcp_server you called, and the tool name and the function name","stream":false}'
```
### Test (streaming example)
```bash
curl -X POST http://localhost:8088/responses \
  -H "Content-Type: application/json" \
  -d '{"input":"use github tool to get latest commit in <repo_name> repo from github, the repo owner is <repo-owner-name>. And please use json format in response and should include mcp_server you called, and the tool name and the function name","stream":true}'
```

### Troubleshooting
| Issue | Cause | Fix |
|-------|-------|-----|
| 401 from MCP tool | Missing / invalid `GITHUB_TOKEN` | Recreate PAT & export to env |
| 401 from Azure model | Invalid Azure AI project endpoint or missing Azure login | Re-check `.env` values and ensure `az login` (or service principal env vars) is active |
| Import errors | Missing package installs / dotenv | Re-run install commands |

### Notes
- Do NOT commit `.env`.
- You can add additional MCP servers by appending more tool instances in `create_agent()`.
