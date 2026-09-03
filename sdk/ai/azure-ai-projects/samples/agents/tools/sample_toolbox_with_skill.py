# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to create a shipping-cost Skill, include it in
    a Toolbox, and use its persisted instructions with a Prompt Agent. The
    Toolbox is exposed to the agent through its versioned MCP endpoint.

    Prompt Agent definitions do not have a native skill-reference field, so the
    sample downloads the immutable Skill version and adds its ``SKILL.md``
    content to the agent instructions. A marker known only to the persisted
    Skill proves that the agent applied those instructions.

USAGE:
    python sample_toolbox_with_skill.py

    Before running the sample:

    pip install "azure-ai-projects>=2.5.0" python-dotenv openai

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) FOUNDRY_MODEL_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
    3) FOUNDRY_AGENT_NAME - Optional. The name of the AI agent. If not set, defaults to "MyAgent".
"""

import io
import os
import zipfile

from dotenv import load_dotenv
from util import create_version_with_endpoint

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    MCPTool,
    PromptAgentDefinition,
    SkillInlineContent,
    ToolSearchToolboxTool,
    ToolboxSkillReference,
)
from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
agent_name = os.environ.get("FOUNDRY_AGENT_NAME") or "MyAgent"

SKILL_NAME = "shipping-cost-skill"
SKILL_PROOF_MARKER = "SHIPPING_COST_SKILL_APPLIED"
TOOLBOX_NAME = "toolbox_with_skill_prompt_agent"
TOOLBOX_MCP_LABEL = "shipping-toolbox"


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
                f"Begin your answer with `{SKILL_PROOF_MARKER}`. Compute shipping cost using "
                "cost (USD) = 5 + 2 * weight_kg for domestic destinations, and "
                "cost (USD) = 15 + 4 * weight_kg for international destinations. "
                "Always state the formula you used."
            ),
            metadata={"revision": "1"},
        ),
    )
    print(f"Created skill `{skill_version.name}` (version {skill_version.version}).")

    try:
        skill_archive = b"".join(
            project_client.beta.skills.download_version(name=skill_version.name, version=skill_version.version)
        )
        with zipfile.ZipFile(io.BytesIO(skill_archive)) as archive:
            skill_instructions = archive.read("SKILL.md").decode("utf-8")
        print(f"Loaded instructions from skill `{skill_version.name}` version {skill_version.version}.")

        toolbox_version = project_client.toolboxes.create_version(
            name=TOOLBOX_NAME,
            description="Toolbox exposing a shipping-cost skill to a Prompt Agent.",
            tools=[ToolSearchToolboxTool(name="skill_search")],
            skills=[ToolboxSkillReference(name=skill_version.name, version=skill_version.version)],
        )
        print(f"Created toolbox `{toolbox_version.name}` (version {toolbox_version.version}).")

        toolbox_mcp_url = f"{endpoint}/toolboxes/{TOOLBOX_NAME}/versions/{toolbox_version.version}/mcp?api-version=v1"
        toolbox_mcp_tool = MCPTool(
            server_label=TOOLBOX_MCP_LABEL,
            server_url=toolbox_mcp_url,
            authorization=credential.get_token("https://ai.azure.com/.default").token,
            require_approval="never",
        )

        with create_version_with_endpoint(
            project_client=project_client,
            agent_name=agent_name,
            definition=PromptAgentDefinition(
                model=os.environ["FOUNDRY_MODEL_NAME"],
                instructions=("Follow the persisted Skill instructions below.\n\n" f"{skill_instructions}"),
                tools=[toolbox_mcp_tool],
            ),
        ):
            user_input = "Compute the shipping cost for a 3 kg package shipped domestically."
            print(f"User: {user_input}")
            response = openai_client.responses.create(input=user_input)

            for item in response.output:
                if item.type == "mcp_list_tools":
                    print(f"server_label={item.server_label}, tools={[tool.name for tool in (item.tools or [])]}")
                elif item.type == "mcp_call":
                    print(f"server_label={item.server_label}, name={item.name}, error={item.error}")
                    print(f"  arguments: {item.arguments}")
                    print(f"  output: {item.output}")

            if SKILL_PROOF_MARKER not in (response.output_text or ""):
                raise RuntimeError("The response did not contain evidence that the skill instructions were applied.")

            print(f"Verified skill instructions with marker `{SKILL_PROOF_MARKER}`.")
            print(f"\nResponse: {response.output_text}")
    finally:
        try:
            project_client.toolboxes.delete(TOOLBOX_NAME)
            print(f"\nDeleted toolbox `{TOOLBOX_NAME}`")
        except ResourceNotFoundError:
            pass
        finally:
            try:
                project_client.beta.skills.delete(SKILL_NAME)
                print(f"Deleted skill `{SKILL_NAME}`")
            except ResourceNotFoundError:
                pass
