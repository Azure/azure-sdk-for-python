"""
DESCRIPTION:
    Defines the Onboarding sub-agent for the SDK Dev Agent. The onboarding
    agent helps first-time users get set up with the azure-ai-projects and
    azure-ai-agents Python SDKs: installing packages, signing in with
    `az login`, setting required environment variables, and walking through
    their first sample. It has Bing grounding for current docs and Code
    Interpreter for running short Python snippets in a sandbox.

    This module exports `onboarding_agent(project)` which creates the agent
    version in Foundry and returns the created Agent object. The orchestrator
    binds it as a callable tool via `bind_onboarding` / `ask_onboarding_tool`
    (see `sdk_dev_agent.tools`).

USAGE:
    Not run directly. Imported by `sdk_dev_agent.agents.orchestrator`.

    Required environment variables (loaded from `.env` by the orchestrator):
    1) FOUNDRY_PROJECT_ENDPOINT   - Foundry project endpoint URL.
    2) FOUNDRY_MODEL_NAME         - Chat model deployment name (e.g. `gpt-4o`).
    3) BING_PROJECT_CONNECTION_ID - Bing grounding connection ID.
"""

import os
from typing import Any

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    BingGroundingSearchConfiguration,
    BingGroundingSearchToolParameters,
    BingGroundingTool,
    CodeInterpreterTool,
    PromptAgentDefinition,
)


def onboarding_agent(project: AIProjectClient) -> Any:
    """Create the Onboarding sub-agent version in Foundry and return the Agent."""
    return project.agents.create_version(
        agent_name="sdk-onboarding-agent",
        definition=PromptAgentDefinition(
            model=os.environ["FOUNDRY_MODEL_NAME"],
            instructions=(
                "You are the SDK Onboarding Agent. You help first-time users get set up "
                "with the azure-ai-projects and azure-ai-agents Python SDKs.\n"
                "\n"
                "When the user wants a tour / overview / summary, give ONE consolidated "
                "answer with headings (Purpose, Where things live, What to read next). "
                "Don't ask 'ready to continue?' — finish the tour in one reply.\n"
                "\n"
                "When the user is performing a multi-step setup task (install, az login, "
                "create resource, run a sample), answer one step at a time and confirm "
                "before moving on.\n"
                "\n"
                "Define jargon. Keep code blocks runnable. Never skip a step the user "
                "hasn't done. Cite source URLs for any external docs."
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
                CodeInterpreterTool(),
            ],
        ),
    )
