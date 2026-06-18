# SDK Dev Agent

An interactive terminal agent that helps you work with the
[`azure-ai-projects`](../README.md) and
[`azure-ai-agents`](../../azure-ai-agents/README.md) SDKs across Python,
JS/TS, and .NET. It is a small orchestrator over three sub-agents built on
top of the Azure AI Foundry Agents service:

| Sub-agent     | What it does                                                              | Tools it uses                  |
| ------------- | ------------------------------------------------------------------------- | ------------------------------ |
| `onboarding`  | First-time setup, install / `az login` / env-vars, walking a first sample | Bing grounding, CodeInterpreter |
| `researcher`  | Real repo content: cross-language compares, "how does this code work"     | GitHub MCP                     |
| `triage`      | Live engineering signal: open PRs, open issues, error-message lookup      | GitHub MCP                     |

The orchestrator itself has Bing grounding for general web lookups and
function-call tools (`ask_onboarding`, `ask_researcher`, `ask_triage`) to
delegate to the three sub-agents. Sub-agent answers are surfaced
verbatim — the orchestrator does not paraphrase them.

## Prerequisites

- Python 3.10+
- Azure CLI (`az login` works) — used by `DefaultAzureCredential`.
- An Azure AI Foundry project with:
  - A deployed chat model (default: `gpt-4o`).
  - A Bing grounding connection.
  - A GitHub MCP connection (server URL `https://api.githubcopilot.com/mcp/`)
    backed by a GitHub PAT with read access to `Azure/azure-sdk-for-python`,
    `Azure/azure-sdk-for-js`, `Azure/azure-sdk-for-net`, and
    `Azure/azure-rest-api-specs`.

## Setup

From this folder (`sdk/ai/azure-ai-projects/sdk-dev-agent`):

```powershell
# 1. Create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Install dependencies and this package (editable)
pip install -r dev_requirements.txt
pip install -e .

# 3. Sign in for DefaultAzureCredential
az login

# 4. Configure environment variables
Copy-Item .env.example .env
# then open .env and fill in the four values below
```

Required variables in `.env`:

| Variable                     | Description                                                                                   |
| ---------------------------- | --------------------------------------------------------------------------------------------- |
| `FOUNDRY_PROJECT_ENDPOINT`   | Foundry project endpoint URL (Foundry portal → your project → Overview).                      |
| `FOUNDRY_MODEL_NAME`         | Chat model deployment name (e.g. `gpt-4o`).                                                   |
| `BING_PROJECT_CONNECTION_ID` | Full resource ID of the Bing grounding connection (Foundry portal → Connections).             |
| `GITHUB_MCP_CONNECTION_ID`   | Name (or full resource ID) of the GitHub MCP custom connection. See section below to create.  |

## Create the GitHub MCP connection

The researcher and triage sub-agents talk to GitHub through the hosted
GitHub MCP server at `https://api.githubcopilot.com/mcp/`. Foundry stores
the authentication for that server in a project-level **custom connection**,
and we pass that connection's name to the SDK as `project_connection_id`.

Do this once per Foundry project:

1. **Create a GitHub Personal Access Token.**
   - Go to [github.com → Settings → Developer settings → Personal access tokens → Fine-grained tokens](https://github.com/settings/personal-access-tokens/new).
   - Resource owner: your user account (or the org if you have one with
     access).
   - Repository access: **Public Repositories (read-only)** is enough —
     all four target repos (`Azure/azure-sdk-for-python`, `-js`, `-net`,
     `azure-rest-api-specs`) are public. No write scopes needed.
   - Permissions: under **Repository permissions**, set `Contents: Read`,
     `Issues: Read`, `Pull requests: Read`, and `Metadata: Read` (the last
     is auto-selected).
   - Generate the token and copy it. You will not be able to view it again.

2. **Create the custom connection in Foundry.**
   - In the [Foundry portal](https://ai.azure.com/) open your project.
   - Go to **Management center → Connections → + New connection**.
   - Pick **Custom keys** (or **Custom connection** depending on the
     portal version).
   - Set:
     - **Connection name**: e.g. `github-mcp` (this is what goes in your
       `.env`).
     - **Endpoint / URL**: `https://api.githubcopilot.com/mcp/`
     - **Authentication**: add a custom key called `Authorization` with
       value `Bearer <your-PAT>` (exactly that, including the word
       `Bearer` and a space). Mark the key as **Is Secret**.
   - Save the connection.

3. **Copy the connection name** (or its full resource ID, both work) into
   `.env` as `GITHUB_MCP_CONNECTION_ID`.

If the researcher or triage sub-agent answers with `Unauthorized` or
`Forbidden`, the PAT is either missing scopes or expired — regenerate it
and update the connection. If the model never calls a GitHub tool, double-
check the connection name in `.env` matches the one in the Foundry portal.

## Run

```powershell
python -m sdk_dev_agent.cli
```

You'll see each sub-agent and the orchestrator print its name and version,
then a `you›` prompt. Type a question and hit enter. Type `exit` or `quit`
to leave; all four agent versions are deleted from Foundry on exit.

If you prefer plain stdout/stdin without the Rich UI:

```powershell
python -m sdk_dev_agent.agents.orchestrator
```

### Example prompts

```
you› How do I install azure-ai-projects and run the basic-agent sample?
you› Compare how to create the AIProjectClient across Python, JS/TS, and .NET.
you› What open PRs touch azure-ai-projects right now?
you› I'm getting `DefaultAzureCredential` 401s — anyone else seeing this?
```

## Project layout

```
sdk-dev-agent/
├── .env.example
├── README.md                 # this file
├── dev_requirements.txt
├── pyproject.toml
└── src/sdk_dev_agent/
    ├── cli.py                # Rich-styled terminal UI wrapper
    ├── agents/
    │   ├── orchestrator.py   # orchestrator agent + chat loop + cleanup
    │   ├── onboarding.py     # Onboarding sub-agent (Bing + CodeInterpreter)
    │   ├── researcher.py     # Researcher sub-agent (GitHub MCP)
    │   └── triage.py         # Triage sub-agent (GitHub MCP)
    └── tools/
        └── tools.py          # bind_* / ask_* / ask_*_tool + trace + dispatch_tools
```

Each `agents/*.py` and `tools/tools.py` has its own DESCRIPTION / USAGE
header docstring with details on what it does and what env vars it needs.
