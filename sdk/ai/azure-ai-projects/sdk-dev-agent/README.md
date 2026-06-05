# SDK Dev Agent

An SDK Dev Agent that helps you work with
[`azure-ai-projects`](../README.md) and
[`azure-ai-agents`](../../azure-ai-agents/README.md) Python SDKs. It can read
files from the local `azure-sdk-for-python` checkout, search the web via
Bing grounding, and run Python in a sandbox via Code Interpreter.

## Prerequisites

- Python 3.10+
- An Azure AI Foundry project with:
  - A deployed chat model (`gpt-4o`).
  - A Bing grounding connection.
- The Azure CLI signed in (`az login`) — used by `DefaultAzureCredential`.

## Setup

From this folder (`sdk/ai/azure-ai-projects/sdk-dev-agent`):

```powershell
# 1. Create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Install dependencies and the package itself (editable)
pip install -r dev_requirements.txt
pip install -e .

# 3. Configure environment variables
Copy-Item .env.example .env
# then edit .env and fill in the three values below
```

Required variables in `.env`:

| Variable                     | Description                                                                 |
| ---------------------------- | --------------------------------------------------------------------------- |
| `FOUNDRY_PROJECT_ENDPOINT`   | Your Foundry project endpoint URL.                                          |
| `FOUNDRY_MODEL_NAME`         | Deployment name of the chat model to use.                                   |
| `BING_PROJECT_CONNECTION_ID` | Full resource ID of the Bing grounding connection in your Foundry project. |

## Run

```powershell
python -m sdk_dev_agent.agents.orchestrator
```

You'll see the agent's name and version, then a `you>` prompt. Type a
question and the agent will respond. Type `exit` or `quit` to leave; the
agent version is cleaned up automatically on exit.

### Example prompts

- "Show me a minimal sample that creates an agent with a code interpreter tool."
- "What's the difference between `AIProjectClient` and `AgentsClient`?"
- "Find the latest async sample for Bing grounding in this repo."

## Project layout

```
src/sdk_dev_agent/
├── agents/
│   └── orchestrator.py     # entry point: builds the agent and runs the chat loop
├── tools/
│   └── tools.py            # local function tools (e.g. read_repo)
└── prompts/                # prompt assets
```
