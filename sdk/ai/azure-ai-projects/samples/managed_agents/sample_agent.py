# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to author and invoke Managed Harness Agents (MHA) using the
    synchronous AIProjectClient. A Managed Harness Agent is a Prompt Agent that opts into a
    Foundry-managed runtime (Brain + Hand, powered by a GitHub Copilot harness) by setting the
    additive `harness=AgentHarness.GITHUB_COPILOT` field on `PromptAgentDefinition`. Everything else about authoring
    and invoking the agent (`/agents` CRUD, `/openai/conversations`, `/openai/responses`) is
    unchanged from a regular Prompt Agent.

    This sample covers 3 hero scenarios, each implemented as its own function:
    1) sample_managed_agent_basic - Author a managed agent and invoke it.
    2) sample_managed_agent_with_skill - Give a managed agent a skill via a Toolbox/MCP tool.
    3) sample_managed_agent_background - Run a long-running managed agent task in the background.

    Scenario 2 assumes a `financial-analysis` skill and a `financial-analysis-toolbox` Toolbox
    that exposes it already exist (see `sample_skills_crud.py` and `sample_toolboxes_crud.py`
    to author them); this sample only looks them up and attaches the Toolbox to the agent.
    Skills and Toolboxes are currently preview features.

USAGE:
    python sample_mha_agent.py

    Before running the sample:

    pip install azure-ai-projects==2.3.0a20260625001 --extra-index-url https://pkgs.dev.azure.com/azure-sdk/public/_packaging/azure-sdk-for-python/pypi/simple
    pip install python-dotenv


    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) FOUNDRY_MODEL_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
"""

import os
import random
import time

from dotenv import load_dotenv

from azure.identity import DefaultAzureCredential

from openai.types.responses import Response

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    MCPTool,
    PromptAgentDefinition,
    AgentHarness
)

load_dotenv()

endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]
model_deployment_name = os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"]

SKILL_NAME = "financial-analysis"
TOOLBOX_NAME = "financial-analysis-toolbox"


def _unique_agent_name(base_name: str) -> str:
    """Append a random suffix to `base_name` so each sample run creates a uniquely named agent."""
    return f"{base_name}-{random.randint(1000, 9999)}"


def _get_final_response(stream) -> "Response":
    """Consume a streamed Responses API call and return the final `Response` object.

    Managed (`harness=AgentHarness.GITHUB_COPILOT`) agents reply with `Content-Type: text/event-stream`, so the
    request must be made with `stream=True` and the events consumed to get the completed
    `Response` (found on the terminal `response.completed` event).
    """
    final_response = None
    for event in stream:
        if event.type == "response.completed":
            final_response = event.response
    if final_response is None:
        raise RuntimeError("Stream ended without a `response.completed` event.")
    return final_response


def _get_started_response(stream) -> "Response":
    """Consume a streamed, `background=True` Responses API call just long enough to get the
    initial `Response` object (id + status), then stop reading the stream.

    Managed (`harness=AgentHarness.GITHUB_COPILOT`) agents reply with `Content-Type: text/event-stream`, so
    `stream=True` is required even for background runs. Returning as soon as the first event
    arrives (rather than reading the whole stream to completion) is what makes the call
    actually return immediately, matching the `background=True` contract.
    """
    for event in stream:
        if event.type in ("response.queued", "response.created", "response.in_progress"):
            return event.response
    raise RuntimeError("Stream ended without a `response.queued`/`response.created` event.")


def sample_managed_agent_basic() -> None:
    """Scenario 1: Author a managed agent and invoke it.

    The call uses the same `create_version` operation as a regular Prompt Agent - the only
    field this adds to the request body is `harness=AgentHarness.GITHUB_COPILOT` on `PromptAgentDefinition`, which
    opts the agent into the Foundry-managed runtime (Brain + Hand) underneath. Omit the field
    (or leave it `null`) to stay on the existing Prompt Agent runtime.
    """
    agent_name = _unique_agent_name("finance-analyst-agent-basic")

    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential, allow_preview=True) as project_client,
    ):

        agent = project_client.agents.create_version(
            agent_name=agent_name,
            definition=PromptAgentDefinition(
                model=model_deployment_name,
                instructions=(
                    "You are a financial analyst agent. Analyze financial statements and "
                    "management commentary to assess earnings quality and flag any red flags."
                ),
                harness=AgentHarness.GITHUB_COPILOT,
            ),
        )
        print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")

        # Create an OpenAI client bound to the agent's own endpoint.
        with project_client.get_openai_client(agent_name=agent_name) as openai_client:

            # Invoke the managed agent through its own endpoint using the Responses protocol.
            # Managed agents reply with an event-stream, so `stream=True` is required.
            stream = openai_client.responses.create(
                stream=True,
                input=(
                    "Analyze the attached financial statements and the management commentary "
                    "for Northwind Robotics. Assess earnings quality and flag any red flags."
                ),
            )
            response = _get_final_response(stream)
            print(f"Response output: {response.output_text}")


def sample_managed_agent_with_skill() -> None:
    """Scenario 2: Give a managed agent a skill.

    Skills are the unit of reusable capability for a managed agent - a named bundle of
    instructions the agent loads when the task matches. This sample assumes the
    `financial-analysis` skill and the `financial-analysis-toolbox` Toolbox that exposes it
    (via a versioned `/mcp` endpoint) already exist - see `sample_skills_crud.py` and
    `sample_toolboxes_crud.py` to author them. Here we just look up the existing Toolbox and
    attach it to the agent as an `MCPTool`. The only managed-agent-specific addition is
    `harness=AgentHarness.GITHUB_COPILOT` on the definition - the skill/toolbox usage is identical to what a Prompt
    Agent uses today.
    """
    agent_name = _unique_agent_name("finance-analyst-agent-skill")

    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential, allow_preview=True) as project_client,
        project_client.get_openai_client() as openai_client,
    ):

        toolbox = project_client.toolboxes.get(name=TOOLBOX_NAME)
        toolbox_mcp_url = (
            f"{endpoint}/toolboxes/{toolbox.name}/versions/{toolbox.default_version}/mcp?api-version=v1"
        )
        toolbox_tool = MCPTool(
            server_label=TOOLBOX_NAME,
            server_url=toolbox_mcp_url,
            authorization=credential.get_token("https://ai.azure.com/.default").token,
            require_approval="never",
        )

        # Create a MANAGED agent that uses the skill. The only managed delta is harness=AgentHarness.GITHUB_COPILOT.
        agent = project_client.agents.create_version(
            agent_name=agent_name,
            definition=PromptAgentDefinition(
                model=model_deployment_name,
                instructions=(
                    f"Answer using the `{SKILL_NAME}` instructions available in your context. "
                    "Apply the skill's red-flag checklist exactly and cite the specific red "
                    "flags you found."
                ),
                temperature=0,
                tools=[toolbox_tool],
                harness=AgentHarness.GITHUB_COPILOT,
            ),
        )
        print(f"Created managed agent {agent.name} (version={agent.version})")

        # Invoke. The skill's instructions are injected into the agent's context.
        # The attached financial statement files are referenced by `file_id` (uploaded ahead
        # of time, e.g. via `openai_client.files.create(file=f, purpose="assistants")`).
        # Managed agents reply with an event-stream, so `stream=True` is required.
        stream = openai_client.responses.create(
            stream=True,
            input=[
                {
                    "type": "message",
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": (
                                "Analyze the attached financial statements and the management "
                                "commentary for Northwind Robotics. Assess earnings quality and "
                                "flag any red flags."
                            ),
                        },
                        {"type": "input_file", "file_id": "assistant-2Uq4eXwQhwarDQNix3ytvQ"},
                        {"type": "input_file", "file_id": "assistant-UJcbhixU4urknnCeDRvNMF"},
                    ],
                }
            ],
            extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
        )
        response = _get_final_response(stream)
        print(f"Response output: {response.output_text}")


def sample_managed_agent_background() -> None:
    """Scenario 3: Run a long-running task in the background.

    Managed agents can run work that takes minutes across many tool calls - a deep analysis, a
    multi-step reconciliation. Rather than holding a request open, create the response with
    `background=True`: the call returns immediately with a `queued` / `in_progress` response
    that the caller polls to a terminal state. Because the managed runtime (PES) checkpoints
    Brain and Hand state, a transient interruption resumes from the last checkpoint instead of
    restarting the run.
    """
    agent_name = _unique_agent_name("finance-analyst-agent-background")

    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential, allow_preview=True) as project_client,
        project_client.get_openai_client() as openai_client,
    ):

        agent = project_client.agents.create_version(
            agent_name=agent_name,
            definition=PromptAgentDefinition(
                model=model_deployment_name,
                instructions=(
                    "You are a financial analyst agent. Analyze financial statements and "
                    "management commentary to assess earnings quality and flag any red flags."
                ),
                harness=AgentHarness.GITHUB_COPILOT,
            ),
        )
        print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")

        # Start a long-running run. `background=True` returns immediately; `store=True` (the
        # default) keeps the response retrievable while it runs. Managed agents reply with an
        # event-stream even for background runs, so `stream=True` is required; we only read the
        # first event (queued/created) so the call returns immediately instead of blocking
        # until the whole run completes.
        with openai_client.responses.create(
            background=True,
            stream=True,
            input=(
                "Analyze the attached financial statements and the management commentary for "
                "Northwind Robotics across every reporting period. Assess earnings quality and "
                "produce a detailed report flagging any red flags."
            ),
            extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
        ) as stream:
            response = _get_started_response(stream)
        print(f"Started background response {response.id} (status={response.status})")

        # Poll to a terminal state. A transient infra interruption is invisible here: PES
        # checkpoints Brain + Hand state and resumes from the last checkpoint rather than
        # restarting.
        while response.status in ("queued", "in_progress"):
            time.sleep(5)
            print(f"Polling response {response.id} (status={response.status})...")
            response = openai_client.responses.retrieve(response_id=response.id)

        if response.status == "completed":
            print(f"Response output: {response.output_text}")
        elif response.status == "failed":
            # On failure the `error` field is populated (e.g. a Hand tool error).
            print(f"Run failed: {response.error.code} - {response.error.message}")
        else:  # incomplete or cancelled
            print(f"Run ended in terminal state: {response.status}")

        # A queued/in-progress background run can also be cancelled:
        # openai_client.responses.cancel(response_id=response.id)


if __name__ == "__main__":
    sample_managed_agent_basic()
    #sample_managed_agent_with_skill()
    #sample_managed_agent_background()