# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to put a shell tool and an inline Skill in a
    Toolbox and use them with a Prompt Agent. The Skill instructs the shell to
    print "Welcome to shell tool" before reporting the Python version and the
    working-directory contents of its auto-provisioned, network-isolated container.

    The sample downloads the persisted Skill's `SKILL.md` into the Prompt Agent
    instructions. The agent reaches the shell through an `MCPTool` pointed at
    the Toolbox's versioned `/mcp` URL. The sample prints the tools exposed by
    the MCP server, each shell command's arguments and output, and the agent's
    final response.

USAGE:
    python sample_toolbox_with_shell_and_skill.py

    Before running the sample:

    pip install "azure-ai-projects>=2.6.0" python-dotenv openai

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
from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    MCPTool,
    PromptAgentDefinition,
    ShellToolboxTool,
    SkillInlineContent,
    ToolSearchToolboxTool,
    ToolboxSkillReference,
    ToolboxShellContainerAutoEnvironment,
)

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]

SKILL_NAME = "sandbox-environment-inspection"
TOOLBOX_NAME = "toolbox_with_shell_tool"
TOOLBOX_MCP_LABEL = "shell-toolbox"
agent_name = os.environ.get("FOUNDRY_AGENT_NAME") or "MyAgent"


with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential, allow_preview=True) as project_client,
    project_client.get_openai_client(agent_name=agent_name) as openai_client,
):
    try:
        project_client.toolboxes.delete(TOOLBOX_NAME)
        print(f"Deleted pre-existing toolbox `{TOOLBOX_NAME}`")
    except ResourceNotFoundError:
        pass

    try:
        project_client.beta.skills.delete(SKILL_NAME)
        print(f"Deleted pre-existing skill `{SKILL_NAME}`")
    except ResourceNotFoundError:
        pass

    skill_version = project_client.beta.skills.create(
        name=SKILL_NAME,
        inline_content=SkillInlineContent(
            description="Inspect the runtime environment of a sandboxed shell container.",
            instructions=(
                "When asked to inspect the sandbox environment, first run "
                "`printf 'Welcome to shell tool\\n'` with the shell tool. Then run the relevant "
                "commands. For Python version and working-directory contents, run "
                "`python --version`, `pwd`, and `ls -la`. Report the exact command output."
            ),
        ),
    )
    print(f"Created skill `{skill_version.name}` (version {skill_version.version}).")

    skill_archive = b"".join(
        project_client.beta.skills.download_version(name=skill_version.name, version=skill_version.version)
    )
    with zipfile.ZipFile(io.BytesIO(skill_archive)) as archive:
        skill_instructions = archive.read("SKILL.md").decode("utf-8")
    print(f"Loaded instructions from skill `{skill_version.name}` version {skill_version.version}.")

    shell_tool = ShellToolboxTool(
        name="shell",
        description="Runs shell commands in a sandboxed container.",
        environment=ToolboxShellContainerAutoEnvironment(),
    )

    try:
        toolbox_version = project_client.toolboxes.create_version(
            name=TOOLBOX_NAME,
            description="Toolbox with a shell tool and an environment-inspection skill.",
            tools=[shell_tool, ToolSearchToolboxTool(name="skill_search")],
            skills=[ToolboxSkillReference(name=skill_version.name, version=skill_version.version)],
        )
        print(f"Created toolbox `{TOOLBOX_NAME}` (version {toolbox_version.version}).")

        toolbox_mcp_url = f"{endpoint}/toolboxes/{TOOLBOX_NAME}/versions/{toolbox_version.version}/mcp?api-version=v1"
        token = credential.get_token("https://ai.azure.com/.default").token

        toolbox_mcp_tool = MCPTool(
            server_label=TOOLBOX_MCP_LABEL,
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
                    "You have a shell tool that runs commands in a sandboxed container with no "
                    "network access. Follow the loaded skill instructions below and report the exact "
                    f"command output back to the user.\n\n{skill_instructions}"
                ),
                tools=[toolbox_mcp_tool],
            ),
        ):
            response = openai_client.responses.create(
                input=(
                    "Use the sandbox environment inspection skill to determine which Python version "
                    "is installed and what is in the working directory."
                ),
            )

            for item in response.output:
                if item.type == "mcp_list_tools":
                    print(f"server_label={item.server_label}, tools={[tool.name for tool in (item.tools or [])]}")
                elif item.type == "mcp_call":
                    print(f"server_label={item.server_label}, name={item.name}, error={item.error}")
                    print(f"  arguments: {item.arguments}")
                    print(f"  output: {item.output}")

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
