# Azure AI Agent Server — GitHub Copilot SDK Adapter

Bridges the [GitHub Copilot SDK](https://github.com/github/copilot-sdk) to the
Azure AI Foundry hosted agent platform, translating between the Copilot SDK's
event model and the Foundry Responses API (RAPI) protocol.

## Getting started

### Install the package

```bash
pip install azure-ai-agentserver-github
```

### Quick start

```python
from azure.ai.agentserver.github import GitHubCopilotAdapter

adapter = GitHubCopilotAdapter.from_project(".")
adapter.run()
```

### Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `AZURE_AI_PROJECT_ENDPOINT` | Yes | Foundry project endpoint |
| `GITHUB_TOKEN` | For dev | Fine-grained PAT with Copilot Requests Read-only scope |
| `AZURE_AI_FOUNDRY_RESOURCE_URL` | For BYOK | Foundry resource URL for Managed Identity auth |
| `COPILOT_MODEL` | No | Model deployment name (default: `gpt-4.1` for BYOK, `gpt-5` for GitHub) |
| `TOOL_ACL_PATH` | Recommended | Path to YAML tool ACL file |

## Key concepts

- **CopilotAdapter**: Core adapter extending `FoundryCBAgent`. Handles BYOK auth,
  n:n event mapping, Tool ACL, OTel traces, streaming, and session management.
- **GitHubCopilotAdapter**: Convenience subclass that adds skill directory discovery
  and conversation history bootstrap for cold starts.
- **ToolAcl**: YAML-based permission system gating shell, read, write, url, and
  mcp operations with regex matching and first-match-wins evaluation.

## Troubleshooting

See the [FAQ](https://github.com/coreai-microsoft/foundry-declarative-agent/blob/main/FAQ.md)
for common issues including expired GitHub PATs, RBAC roles, and deployment gotchas.

## Contributing

This project welcomes contributions and suggestions. See [CONTRIBUTING.md](https://github.com/Azure/azure-sdk-for-python/blob/main/CONTRIBUTING.md).
