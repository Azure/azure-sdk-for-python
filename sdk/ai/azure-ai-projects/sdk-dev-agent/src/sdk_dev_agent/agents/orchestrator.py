"""
DESCRIPTION:
    Orchestrator for the SDK Dev Agent. Creates three sub-agents
    (onboarding, researcher, triage) and the orchestrator agent in
    Foundry, runs a chat loop on the terminal, and routes each
    user message to the right sub-agent via function-call tools. The
    orchestrator uses the Bing grounding tool for general web lookups.

USAGE:
    python -m sdk_dev_agent.cli      #  terminal UI option
    python -m sdk_dev_agent.agents.orchestrator   

    Before running:

    pip install -r dev_requirements.txt
    pip install -e .
    az login

    Required environment variables (loaded from `.env` via `python-dotenv`):
    1) FOUNDRY_PROJECT_ENDPOINT   - Foundry project endpoint URL.
    2) FOUNDRY_MODEL_NAME         - Chat model deployment name (e.g. `gpt-4o`).
    3) BING_PROJECT_CONNECTION_ID - Bing grounding connection ID (used by
                                    orchestrator and onboarding sub-agent).
    4) GITHUB_MCP_CONNECTION_ID   - GitHub MCP connection ID (used by
                                    researcher and triage sub-agents).
"""

import os

from dotenv import load_dotenv

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    BingGroundingSearchConfiguration,
    BingGroundingSearchToolParameters,
    BingGroundingTool,
    PromptAgentDefinition,
)

from ..tools import (
    ask_onboarding_tool,
    ask_researcher_tool,
    ask_triage_tool,
    bind_onboarding,
    bind_researcher,
    bind_triage,
    dispatch_tools,
    trace,
)
from .onboarding import onboarding_agent
from .researcher import researcher_agent
from .triage import triage_agent

load_dotenv()


with (
    DefaultAzureCredential() as credential,
    AIProjectClient(
        endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        credential=credential,
    ) as project,
    project.get_openai_client() as openai_client,
):
    onboarding = onboarding_agent(project)
    bind_onboarding(openai_client, onboarding.name)
    print(f"Onboarding sub-agent: {onboarding.name} v{onboarding.version}")
    researcher = researcher_agent(project)
    bind_researcher(openai_client, researcher.name)
    print(f"Researcher sub-agent: {researcher.name} v{researcher.version}")
    triage = triage_agent(project)
    bind_triage(openai_client, triage.name)
    print(f"Triage sub-agent: {triage.name} v{triage.version}")
    agent = project.agents.create_version(
        agent_name="sdk-dev-agent",
        definition=PromptAgentDefinition(
            model=os.environ["FOUNDRY_MODEL_NAME"],
            instructions=(
                "You are the SDK Dev Agent. You help users with the azure-ai-projects "
                "and azure-ai-agents SDKs across Python, JS/TS, and .NET, plus the "
                "TypeSpec specs in azure-rest-api-specs.\n"
                "\n"
                "## Routing (pick ONE)\n"
                "1. **Reading SDK source code** \u2014 cross-language compares, "
                "'how does this method work', spec-vs-code, inconsistency checks: "
                "call `ask_researcher` and present its `answer` verbatim.\n"
                "2. **Live engineering signal** \u2014 open PRs, open issues, recent "
                "activity, diagnosing an error message against existing issues: call "
                "`ask_triage` and present its `answer` verbatim.\n"
                "3. **First-time setup** \u2014 install, az login, env vars, run first "
                "sample: call `ask_onboarding` and present its `answer` verbatim.\n"
                "4. **Release notes / changelogs / 'what changed in version X' / "
                "current external docs / blog posts**: use Bing directly. These are "
                "published as web pages on PyPI, npm, NuGet, GitHub releases, and "
                "learn.microsoft.com \u2014 don't route to the researcher for them. "
                "Cite URLs.\n"
                "5. **Greetings, capability questions, clarifications**: answer "
                "directly, no tools.\n"
                "\n"
                "## Hard rules\n"
                "- Never invent class names, methods, paths, or CHANGELOG entries. If "
                "a subagent or Bing says it couldn't find something, surface that "
                "\u2014 do not fill in from memory.\n"
                "- If a subagent returns an `error`, do NOT keep retrying with "
                "rephrased questions. Tell the user what failed and ask them to "
                "clarify.\n"
                "- Don't ask permission to use a tool. Just use it."
            ),
            tools=[
                BingGroundingTool(
                    bing_grounding=BingGroundingSearchToolParameters(
                        search_configurations=[
                            BingGroundingSearchConfiguration(
                                project_connection_id=os.environ["BING_PROJECT_CONNECTION_ID"],
                            )
                        ]
                    )
                ),
                ask_researcher_tool(),
                ask_triage_tool(),
                ask_onboarding_tool(),
            ],
        ),
    )
    print(f"Agent: {agent.name} v{agent.version}")
    print("Type a message (or 'exit'/'quit' to leave).\n")

    try:
        previous_id = None
        while True:
            try:
                user_msg = input("you> ").strip()
            except EOFError:
                break
            if not user_msg:
                continue
            if user_msg.lower() in {"exit", "quit"}:
                break

            try:
                response = openai_client.responses.create(
                    input=user_msg,
                    extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
                    **({"previous_response_id": previous_id} if previous_id else {}),
                )
                trace(response)
                verbatim: str | None = None
                for _ in range(10):
                    outputs, vb = dispatch_tools(response)
                    if vb and not verbatim:
                        verbatim = vb
                    if not outputs:
                        break
                    response = openai_client.responses.create(
                        input=outputs,
                        previous_response_id=response.id,
                        extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
                    )
                    trace(response)
            except Exception as exc:
                print(f"\nagent> [request failed: {type(exc).__name__}: {exc}]\n")
                continue

            previous_id = response.id
            print(f"\nagent> {verbatim if verbatim else response.output_text}\n")
    finally:
        try:
            project.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
            print(f"Deleted {agent.name} v{agent.version}")
        except Exception as exc:
            print(f"Cleanup failed for {agent.name}: {exc}")
        try:
            project.agents.delete_version(agent_name=researcher.name, agent_version=researcher.version)
            print(f"Deleted {researcher.name} v{researcher.version}")
        except Exception as exc:
            print(f"Cleanup failed for {researcher.name}: {exc}")
        try:
            project.agents.delete_version(agent_name=triage.name, agent_version=triage.version)
            print(f"Deleted {triage.name} v{triage.version}")
        except Exception as exc:
            print(f"Cleanup failed for {triage.name}: {exc}")
        try:
            project.agents.delete_version(agent_name=onboarding.name, agent_version=onboarding.version)
            print(f"Deleted {onboarding.name} v{onboarding.version}")
        except Exception as exc:
            print(f"Cleanup failed for {onboarding.name}: {exc}")
