# Azure AI Agent Server Adapter for GitHub Copilot SDK for Python

Bridges the [GitHub Copilot SDK](https://github.com/github/copilot-sdk) to the
Azure AI Foundry hosted agent platform, translating between the Copilot SDK's
event model and the Foundry Responses API (RAPI) protocol.

## Getting started

### Prerequisites

- **Python 3.10+**
- **Azure AI Foundry project** with hosted agents enabled (ADC / vNext)
- **Authentication** — one of:
  - A [GitHub fine-grained PAT](https://github.com/settings/personal-access-tokens/new) with **Copilot Requests Read-only** scope (for development)
  - An Azure AI Foundry resource URL for Bring Your Own Key (BYOK) / Managed Identity auth (for production)
- **Azure CLI** (`az login`) for deployment scripts

### Install the package

```bash
pip install azure-ai-agentserver-ghcopilot
```

### Quick start

```python
from dotenv import load_dotenv
load_dotenv()

from azure.ai.agentserver.githubcopilot import GitHubCopilotAdapter

adapter = GitHubCopilotAdapter.from_project(".")
adapter.run()
```

### Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `FOUNDRY_PROJECT_ENDPOINT` | Yes | Foundry project endpoint (e.g., `https://<resource>.services.ai.azure.com/api/projects/<project>`). Falls back to `AZURE_AI_PROJECT_ENDPOINT` if not set. |
| `GITHUB_TOKEN` | For dev | Fine-grained PAT with Copilot Requests Read-only scope |
| `AZURE_AI_FOUNDRY_RESOURCE_URL` | For BYOK | Foundry resource URL for Managed Identity auth (e.g., `https://<resource>.cognitiveservices.azure.com`) |
| `AZURE_AI_FOUNDRY_API_KEY` | Optional | Static API key (skips Managed Identity) |
| `AZURE_AI_FOUNDRY_MODEL` | Optional | Override model deployment name (bypasses auto-discovery) |
| `COPILOT_MODEL` | No | Model name (default: `gpt-4.1` for BYOK, `gpt-5` for GitHub) |
| `TOOL_ACL_PATH` | Optional | Path to YAML tool ACL file (see Tool ACL section below) |
| `LOG_LEVEL` | No | Set to `DEBUG` for verbose container logs |

## Key concepts

### CopilotAdapter vs GitHubCopilotAdapter

- **`CopilotAdapter`**: Low-level adapter extending `FoundryCBAgent`. Use this when you
  need full control over skill directories and session config, or when building a
  custom adapter on top of the Copilot SDK bridge.
- **`GitHubCopilotAdapter`**: Recommended for most developers. Extends `CopilotAdapter`
  with automatic skill directory discovery (`.github/skills/*/SKILL.md` or
  `*/SKILL.md`) and conversation history bootstrap on cold starts so multi-turn
  context is preserved across container restarts.

### Authentication modes

**GitHub token (development):** Set `GITHUB_TOKEN` with a fine-grained PAT. The
Copilot SDK uses this to authenticate with GitHub's Copilot API.

**BYOK / Managed Identity (production):** Set `AZURE_AI_FOUNDRY_RESOURCE_URL`
to your Foundry resource endpoint. "BYOK" stands for Bring Your Own Key — the
adapter uses `DefaultAzureCredential` to obtain tokens for the
`cognitiveservices.azure.com` scope and passes them to the Copilot SDK. No
GitHub token needed. You can also pass a custom credential instance via the
`credential` parameter to override `DefaultAzureCredential`.

### Tool ACL

The optional YAML-based Tool Access Control List gates which operations the
Copilot SDK agent can perform. Rules are evaluated in declaration order;
first match wins; the default action is configurable (`allow` or `deny`).

Five permission kinds are supported: `shell` (commands), `read` (files),
`write` (files), `url` (HTTP), and `mcp` (MCP tool calls). Patterns use
Python regex syntax.

**If no Tool ACL is configured** (`TOOL_ACL_PATH` not set), all tool requests
are auto-approved.

Example `tools_acl.yaml`:

```yaml
version: "1"
default: deny
rules:
  - kind: read
    pattern: ".*"
    action: allow
  - kind: shell
    pattern: "^(ls|cat|head|grep) "
    action: allow
```

> **Note:** Tool ACL is an interim feature and may be removed from this package
> in a future release when equivalent functionality is available in the Copilot SDK.

## Examples

### Minimal agent

```python
from dotenv import load_dotenv
load_dotenv()

from azure.ai.agentserver.githubcopilot import GitHubCopilotAdapter

adapter = GitHubCopilotAdapter.from_project(".")
adapter.run()
```

### With custom credential

```python
from azure.identity import ManagedIdentityCredential
from azure.ai.agentserver.githubcopilot import GitHubCopilotAdapter

credential = ManagedIdentityCredential()
adapter = GitHubCopilotAdapter.from_project(".", credential=credential)
adapter.run()
```

### With explicit skill directories

```python
from azure.ai.agentserver.githubcopilot import GitHubCopilotAdapter

adapter = GitHubCopilotAdapter(
    skill_directories=["/app/skills"],
    project_root="/app",
)
adapter.run()
```

## Troubleshooting

### Agent hangs for 120 seconds and times out

**Check your `GITHUB_TOKEN` first.** The Copilot SDK gives no error for expired
or invalid tokens — it silently hangs. `send_and_wait` waits for `session.idle`
that never arrives, timing out after 120 seconds. This looks identical to a
networking issue.

**Fix:** Generate a new fine-grained PAT with Copilot Requests Read-only scope.

### `session_not_ready` on first invocation

This is a normal cold start. ADC provisions a new micro VM and starts the
container (~10–20 seconds). Wait 30 seconds and retry.

If it persists, check:
- Container build logs for import errors
- Workspace string is ≤63 characters (Kubernetes label limit)
- Agent name isn't "poisoned" from a prior failed deployment (try a new name)

### RBAC roles

| Identity | Role | Scope |
|----------|------|-------|
| Project managed identity | `Container Registry Repository Reader` | ACR |
| Shared Agent Identity | `Azure AI User` | Foundry resource |
| Shared Agent Identity | `Cognitive Services OpenAI User` | Foundry resource |

**Common mistake:** Using `AcrPull` instead of `Container Registry Repository Reader` —
similar names, different permissions.

### Shared Agent Identity prerequisite

Hosted agents fail silently until you create any prompt agent on the project first
(triggers Entra identity provisioning). Without it, agent creation succeeds but
invocation returns `server_error`.

## Next steps

- See `INSTRUCTIONS.md` in the package source for a detailed setup guide, contributing, and troubleshooting
- See `CHANGELOG.md` in the package source for release history
- [Azure AI Foundry documentation](https://learn.microsoft.com/azure/ai-studio/)

## Contributing

This project welcomes contributions and suggestions. See [CONTRIBUTING.md](https://github.com/Azure/azure-sdk-for-python/blob/main/CONTRIBUTING.md).
