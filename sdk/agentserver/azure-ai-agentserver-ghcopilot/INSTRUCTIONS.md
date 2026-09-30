# azure-ai-agentserver-ghcopilot — Getting Started

Instructions for using, testing, and contributing to the GitHub Copilot SDK adapter package for Azure AI Agent Server.

---

## Overview

This package bridges the GitHub Copilot SDK to Azure AI Foundry's hosted agent platform. It translates between the Copilot SDK's event model and the Foundry Responses API (RAPI) protocol.

**Hero code sample:**

```python
from azure.ai.agentserver.githubcopilot import GitHubCopilotAdapter

adapter = GitHubCopilotAdapter.from_project(".")
adapter.run()
```

That's it — skill discovery, session management, auth, and RAPI event mapping are handled automatically.

---

## Package Structure

```
azure-ai-agentserver-ghcopilot/
├── azure/ai/agentserver/githubcopilot/
│   ├── __init__.py                    ← Public API: GitHubCopilotAdapter, CopilotAdapter, ToolAcl
│   ├── _copilot_adapter.py            ← Core + convenience adapter classes
│   ├── _copilot_request_converter.py  ← RAPI request → Copilot prompt + attachments
│   ├── _copilot_response_converter.py ← Copilot events → RAPI SSE events
│   ├── _tool_acl.py                   ← YAML-based tool permission system
│   └── _version.py                    ← Package version (1.0.0b1)
├── tests/
│   ├── integration/                   ← End-to-end ADC deploy/invoke tests
│   │   ├── test_agent/                ← Minimal test agent (5-line main.py)
│   │   ├── deploy.py                  ← Build + deploy to ADC
│   │   ├── invoke.py                  ← Invoke deployed agent
│   │   ├── logs.py                    ← Stream container logs
│   │   └── README.md
│   └── __init__.py
├── pyproject.toml
├── README.md
└── CHANGELOG.md
```

---

## Relationship to foundry-declarative-agent

This package is the **production home** for the adapter code that previously lived in `coreai-microsoft/foundry-declarative-agent` under `.foundry/runtime/vendor/`.

| | foundry-declarative-agent | This package |
|---|---|---|
| **Purpose** | Reference repo with example agents, deploy scripts, skills | The adapter library itself |
| **Adapter code** | Vendored in `.foundry/runtime/vendor/` | First-party in `azure/ai/agentserver/githubcopilot/` |
| **How agents use it** | Copies vendor code into container | `pip install azure-ai-agentserver-ghcopilot` |
| **Where it ships** | Not shipped — internal reference | Ships via Azure SDK pipeline |

Going forward, adapter code changes should be made here. The foundry-declarative-agent repo will eventually consume this package via `pip install` instead of vendoring.

---

## Prerequisites

1. **Azure CLI** — `az login` authenticated
2. **Subscription allowlisted** for vNext hosted agents (NCUS region)
3. **ACR** with correct RBAC (see below)
4. **Shared Agent Identity** provisioned (create any prompt agent in Foundry UI first)
5. **GitHub PAT** — fine-grained, Copilot Requests Read-only scope
6. **Python 3.10+** with package dependencies installed locally (for validation)

### RBAC Roles Required

**On the ACR:**

| Identity | Role |
|----------|------|
| Project's system-assigned managed identity | `Container Registry Repository Reader` (NOT `AcrPull`) |

**On the Foundry resource:**

| Identity | Role |
|----------|------|
| Shared Agent Identity | `Azure AI User` |
| Shared Agent Identity | `Cognitive Services OpenAI User` |

---

## Local Development Setup

Install the package and its dependencies locally for validation and testing:

```bash
cd sdk/agentserver/azure-ai-agentserver-ghcopilot
pip install --pre -e ".[dev]" 2>/dev/null || pip install --pre azure-ai-agentserver-core github-copilot-sdk==0.2.0 azure-identity PyYAML python-dotenv
```

### Validate Before Deploying

Always run these checks before any deploy:

```bash
# Syntax check
python -c "
import py_compile, sys
for f in ['azure/ai/agentserver/githubcopilot/_copilot_adapter.py',
          'azure/ai/agentserver/githubcopilot/_copilot_response_converter.py',
          'azure/ai/agentserver/githubcopilot/_copilot_request_converter.py',
          'azure/ai/agentserver/githubcopilot/_tool_acl.py']:
    py_compile.compile(f, doraise=True)
    print(f'  OK  {f}')
print('Syntax OK')
"

# Import check (catches missing deps, broken references)
python -c "from azure.ai.agentserver.githubcopilot import GitHubCopilotAdapter; print('Imports OK')"
```

---

## Integration Testing on ADC

The `tests/integration/` directory contains a minimal test agent and scripts to deploy/invoke/stream logs on ADC.

### 1. Configure Environment

Create a `.env` file at the package root:

```
AZURE_AI_PROJECT_ENDPOINT=https://<account>.services.ai.azure.com/api/projects/<project>
GITHUB_TOKEN=github_pat_...
ENABLE_APPLICATION_INSIGHTS_LOGGER=false
```

Optional — enable debug logging in the container:
```
LOG_LEVEL=DEBUG
```

### 2. Deploy the Test Agent

```bash
python tests/integration/deploy.py --name pkg-test-01 --acr <your-acr-name>
```

This:
1. Stages the test agent + package source into a build context
2. Builds via ACR Tasks (cloud build, no local Docker needed)
3. Creates the agent on Foundry with vNext experience
4. Waits for the agent to be ready

### 3. Invoke

```bash
python tests/integration/invoke.py --name pkg-test-01 --message "hello"
```

> First invocation may return `session_not_ready` (cold start). Wait ~20 seconds and retry.

### 4. Check Logs

```bash
python tests/integration/logs.py --name pkg-test-01 --session <session-id-from-invoke>
```

With `LOG_LEVEL=DEBUG` in `.env`, this shows full Copilot SDK event data, Azure Identity credential resolution, and HTTP request/response details.

---

## Using This Package in Your Own Agent

### Minimal Agent (5 lines)

```python
# main.py
import logging, os
from dotenv import load_dotenv
load_dotenv(override=False)
logging.basicConfig(level=getattr(logging, os.environ.get("LOG_LEVEL", "INFO").upper(), logging.INFO))

from azure.ai.agentserver.githubcopilot import GitHubCopilotAdapter
adapter = GitHubCopilotAdapter.from_project(".")
adapter.run()
```

### With Custom Skills

Place skills in `skills/<name>/SKILL.md` or `.github/skills/<name>/SKILL.md`. The adapter auto-discovers them:

```
my-agent/
├── main.py
├── AGENTS.md              ← Agent persona/system prompt
├── skills/
│   ├── my-skill/SKILL.md
│   └── another/SKILL.md
├── Dockerfile
├── requirements.txt       ← includes azure-ai-agentserver-ghcopilot
└── .env
```

### Dockerfile

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . /app/
RUN pip install --pre -r requirements.txt
EXPOSE 8088
CMD bash -c '\
  if [ -f /etc/ssl/certs/adc-egress-proxy-ca.crt ]; then \
    cat /etc/ssl/certs/adc-egress-proxy-ca.crt >> /etc/ssl/certs/ca-certificates.crt && \
    cat /etc/ssl/certs/adc-egress-proxy-ca.crt >> $(python -c "import certifi; print(certifi.where())"); \
  fi && \
  python main.py'
```

The egress proxy cert fix is required for all outbound HTTPS on ADC containers.

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `AZURE_AI_PROJECT_ENDPOINT` | Yes (deploy) | Foundry project endpoint |
| `GITHUB_TOKEN` | For dev | Fine-grained PAT, Copilot Requests Read-only |
| `AZURE_AI_FOUNDRY_RESOURCE_URL` | For BYOK | Foundry resource URL for Managed Identity auth |
| `AZURE_AI_FOUNDRY_API_KEY` | Optional | Static API key (skips Managed Identity) |
| `COPILOT_MODEL` | No | Model name (default: `gpt-5` for GitHub, `gpt-4.1` for BYOK) |
| `TOOL_ACL_PATH` | Recommended | Path to YAML tool ACL file |
| `LOG_LEVEL` | No | `DEBUG` for verbose logs, `INFO` (default) for normal |
| `ENABLE_APPLICATION_INSIGHTS_LOGGER` | No | `false` to disable App Insights discovery |

---

## Authentication Modes

### GitHub Token (development)
Set `GITHUB_TOKEN` — uses GitHub's Copilot models. Simplest setup, no Azure resources needed for model inference.

### BYOK / Managed Identity (production)
Set `AZURE_AI_FOUNDRY_RESOURCE_URL` without an API key — uses `DefaultAzureCredential` to get an Entra ID token for `cognitiveservices.azure.com` scope. Works with Managed Identity on ADC containers.

### BYOK / API Key (local dev with Foundry models)
Set both `AZURE_AI_FOUNDRY_RESOURCE_URL` and `AZURE_AI_FOUNDRY_API_KEY` — static API key, no browser flow needed.

---

## SDK Version Pinning

The Copilot SDK is pinned to `github-copilot-sdk==0.2.0` in `pyproject.toml`. This avoids random breakage from SDK updates — the SDK has shipped breaking changes between minor versions (import paths, API signatures).

Bump the version deliberately and test before merging.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `session_not_ready` on first invoke | Normal cold start. Wait 20s, retry. |
| `ImportError: cannot import name 'PermissionRequestResult'` | SDK version mismatch. The adapter has fallback imports — make sure `github-copilot-sdk==0.2.0` is installed. |
| Container starts but hangs for 120s | Expired `GITHUB_TOKEN`. The SDK gives zero error — just a silent timeout. Regenerate the PAT. |
| `AttributeError: 'Starlette' object has no attribute 'on_event'` | Starlette 1.0 removed `on_event`. The adapter handles this — make sure you have the latest code. |
| Agent name "poisoned" after failed deploy | Platform caches first image pull failure per name. Deploy with a new name. |
| `Container Registry Repository Reader` vs `AcrPull` | Use `Repository Reader` — `AcrPull` does NOT work with the hosted agent platform. |

---

## Contributing

1. Get access: follow steps at `aka.ms/jointhesdk` (join Microsoft + Azure orgs, request Azure SDK Partners)
2. Branch from `feature/agentserver-githubcopilot`
3. Make changes, validate locally (syntax + import checks)
4. Deploy and test on ADC before pushing
5. PR against the feature branch

The adapter code is in `azure/ai/agentserver/githubcopilot/`. Files prefixed with `_` are private implementation. The public API is exported from `__init__.py`.
