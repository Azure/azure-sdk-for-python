# Integration Tests

End-to-end tests that deploy a minimal agent to Azure AI Foundry ADC
and verify the `azure-ai-agentserver-ghcopilot` package works in a real
hosted agent environment.

## Prerequisites

- Azure CLI authenticated (`az login`)
- An allowlisted subscription for ADC vNext
- An ACR in NCUS with proper RBAC (see main repo FAQ)
- A `.env` file with `AZURE_AI_PROJECT_ENDPOINT` and `GITHUB_TOKEN`

## Usage

Create a `.env` file in this directory or `test_agent/`:

```
AZURE_AI_PROJECT_ENDPOINT=https://<account>.services.ai.azure.com/api/projects/<project>
GITHUB_TOKEN=github_pat_...
```

Deploy:

```bash
python tests/integration/deploy.py --name pkg-test-01 --acr hav2ncusacr
```

Invoke:

```bash
python tests/integration/invoke.py --name pkg-test-01 --message "hello"
```

## What's tested

- Package installs correctly via `pip install` (no vendored code)
- `GitHubCopilotAdapter.from_project(".")` discovers skills
- Agent starts on port 8088, passes health checks
- Non-streaming invocation returns correct response
- Copilot SDK session creation works with keyword-only API (rc4+)
