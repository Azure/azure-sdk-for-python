# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to expose a Skill to a Prompt Agent via a
    Toolbox, using the synchronous AIProjectClient and the OpenAI-compatible
    client.

    It creates a Skill with inline content describing how to compute shipping
    cost, then creates a Toolbox version that references the skill. A Prompt
    Agent is created with an `MCPTool` pointed at the toolbox's versioned
    `/mcp` endpoint. The skill's instructions are injected into the agent's
    context, so when asked a shipping-cost question the agent answers directly
    using the skill's formula.

    Skills are currently a preview features. In the Python SDK,
    you access these operations via `project_client.beta.skills`.

USAGE:
    python sample_agent_toolbox_skill.py

    Before running the sample:

    pip install "azure-ai-projects>=2.3.0" python-dotenv openai

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the
       Overview page of your Microsoft Foundry portal.
    2) FOUNDRY_MODEL_NAME - The deployment name of the AI model, as found under
       the "Name" column in the "Models + endpoints" tab in your Microsoft
       Foundry project.
    3) FOUNDRY_AGENT_NAME - Optional. The name of the AI agent. If not set, defaults to "MyAgent".
"""

import os

from dotenv import load_dotenv

from azure.ai.projects.models._models import ToolboxSearchPreviewToolboxTool
from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    MCPTool,
    PromptAgentDefinition,
    SkillInlineContent,
    ToolboxSearchPreviewToolboxTool,
    ToolboxSkillReference,
)
from util import create_version_with_endpoint

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]

SKILL_NAME = "shipping-cost-skill"
TOOLBOX_NAME = "toolbox_with_skill"
agent_name = os.environ.get("FOUNDRY_AGENT_NAME", "MyAgent")


with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    project_client.get_openai_client(agent_name=agent_name) as openai_client,
):

    try:
        project_client.toolboxes.delete(TOOLBOX_NAME)
    except ResourceNotFoundError:
        pass

    try:
        project_client.beta.skills.delete(SKILL_NAME)
    except ResourceNotFoundError:
        pass

    skill_version = project_client.beta.skills.create(
        name=SKILL_NAME,
        inline_content=SkillInlineContent(
            description="Compute shipping cost for a package given weight and destination.",
            instructions=(
                "You are a shipping cost calculator. When asked to compute "
                "shipping cost, use this formula: cost (USD) = 5 + 2 * weight_kg "
                "for domestic destinations, and cost (USD) = 15 + 4 * weight_kg "
                "for international destinations. Always state the formula you used."
            ),
            metadata={"revision": "1"},
        ),
    )
    print(f"Created skill: {skill_version.name} version={skill_version.version}")

    toolbox_version = project_client.toolboxes.create_version(
        name=TOOLBOX_NAME,
        description="Toolbox exposing a shipping-cost skill.",
        tools=[ToolboxSearchPreviewToolboxTool()],
        skills=[ToolboxSkillReference(name=skill_version.name, version=skill_version.version)],
    )
    print(f"Created toolbox: {toolbox_version.name} version={toolbox_version.version}")

    toolbox_mcp_url = f"{endpoint}/toolboxes/{TOOLBOX_NAME}/versions/{toolbox_version.version}/mcp?api-version=v1"
    token = credential.get_token("https://ai.azure.com/.default").token

    toolbox_mcp_tool = MCPTool(
        server_label="skill-toolbox",
        server_url=toolbox_mcp_url,
        authorization=token,
        require_approval="never",
    )

    with create_version_with_endpoint(
        project_client=project_client,
        agent_name=agent_name,
        definition=PromptAgentDefinition(
            model=os.environ["FOUNDRY_MODEL_NAME"],
            instructions=(
                "Answer the user using the `shipping-cost-skill` instructions "
                "available in your context. Do not call `tool_search`; the "
                "skill rules are already part of your knowledge. Apply the "
                "skill's formula exactly as given and state the formula in "
                "your answer."
            ),
            temperature=0,
            tools=[toolbox_mcp_tool],
        ),
    ) as agent:

        user_input = "Compute the shipping cost for a 3 kg package shipped domestically."
        print(f"User: {user_input}")
        response = openai_client.responses.create(
            input=user_input,
        )

        for item in response.output:
            if item.type == "mcp_list_tools":
                print(f"mcp_list_tools server_label={item.server_label} tools={[t.name for t in (item.tools or [])]}")
            elif item.type == "mcp_call":
                print(f"mcp_call server_label={item.server_label} name={item.name} error={item.error}")
                if getattr(item, "output", None):
                    print(f"  output: {item.output}")
            elif item.type == "mcp_approval_request":
                print(f"mcp_approval_request server_label={item.server_label} name={item.name}")
            else:
                print(f"output item type={item.type}")

        print(f"Response: {response.output_text}")

    project_client.toolboxes.delete(TOOLBOX_NAME)
    print("Toolbox deleted")
    project_client.beta.skills.delete(SKILL_NAME)
    print("Skill deleted")
