# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Demonstrates deploying a code-based Hosted Agent that discovers and uses
    skills from a Foundry Toolbox MCP endpoint via Agent Framework
    ``SkillsProvider(MCPSkillsSource(...))``.

    The sample:
    1. Creates a shipping-cost skill.
    2. Creates a toolbox version that references the skill.
    3. Packages ``assets/toolbox-agent/`` source as a zip at runtime
       (REMOTE_BUILD - the service resolves dependencies from requirements.txt).
    4. Deploys a new Hosted Agent version, forwarding the project endpoint,
       model name, and toolbox MCP URL to the hosted code.
    5. Waits for the version to become active.
    6. Sends a query to the agent via the Responses API.
    7. Cleans up created resources (agent version, toolbox, and skill).

    The hosted agent must already exist; create it first with:
        samples/hosted_agents/sample_create_hosted_agent.py

USAGE:
    python sample_toolbox_with_skill.py

    Before running the sample:

    pip install "azure-ai-projects>=2.3.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the
       Overview page of your Microsoft Foundry portal.
    2) FOUNDRY_MODEL_NAME - The deployment name of the AI model, as found under
       the "Name" column in the "Models + endpoints" tab in your Foundry project.
    3) FOUNDRY_HOSTED_AGENT_NAME - The Hosted Agent name. Must already exist.
    4) AZURE_SUBSCRIPTION_ID - Azure subscription ID where the Azure AI account
       and project are deployed.
"""

import os
import sys
from pathlib import Path

_SAMPLES_DIR = Path(__file__).resolve().parents[1]
if str(_SAMPLES_DIR) not in sys.path:
    sys.path.insert(0, str(_SAMPLES_DIR))

from dotenv import load_dotenv

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    CodeConfiguration,
    CodeDependencyResolution,
    CreateAgentVersionFromCodeContent,
    CreateAgentVersionFromCodeMetadata,
    HostedAgentDefinition,
    ProtocolVersionRecord,
)

from hosted_agents_util import wait_for_agent_version_active
from rbac_util import ensure_agent_identity_rbac
from util import zip

from azure.core.exceptions import ResourceNotFoundError
from azure.ai.projects.models import (
    SkillInlineContent,
    ToolboxSearchPreviewToolboxTool,
    ToolboxSkillReference,
)

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
model_name = os.environ["FOUNDRY_MODEL_NAME"]
agent_name = os.environ["FOUNDRY_HOSTED_AGENT_NAME"]
subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]

_HOSTED_AGENT_SOURCE_DIR = Path(__file__).parent / "assets" / "toolbox-agent"

SKILL_NAME = "shipping-cost-skill"
TOOLBOX_NAME = "toolbox_with_skill"


def main() -> None:
    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential, allow_preview=True) as project_client,
        project_client.get_openai_client(agent_name=agent_name) as hosted_openai_client,
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

        zip_filename = "hosted-toolbox-agent.zip"
        zip_bytes, zip_sha256, _ = zip(_HOSTED_AGENT_SOURCE_DIR, zip_filename)

        # The ``code`` field accepts any variant of the SDK's ``FileType`` union.
        # The 3-tuple form used here pins both the filename and the content type.
        #
        #   # 1) bare IO[bytes] - filename derived from the file handle's `.name`
        #   code=zip_path.open("rb")
        #
        #   # 2) (filename, bytes)
        #   code=(zip_filename, zip_bytes)
        #
        #   # 3) (filename, IO[bytes])
        #   code=(zip_filename, zip_path.open("rb"))
        #
        #   # 4) (filename, bytes, content_type)
        #   code=(zip_filename, zip_bytes, "application/zip")
        code = (zip_filename, zip_bytes, "application/zip")

        content = CreateAgentVersionFromCodeContent(
            metadata=CreateAgentVersionFromCodeMetadata(
                description="Hosted agent code for toolbox MCP skills with shipping-cost skill.",
                definition=HostedAgentDefinition(
                    cpu="0.5",
                    memory="1Gi",
                    code_configuration=CodeConfiguration(
                        runtime="python_3_14",
                        entry_point=["python", "main.py"],
                        dependency_resolution=CodeDependencyResolution.REMOTE_BUILD,
                    ),
                    environment_variables={
                        "FOUNDRY_PROJECT_ENDPOINT": endpoint,
                        "FOUNDRY_MODEL_NAME": model_name,
                        "MCP_SERVER_URL": toolbox_mcp_url,
                    },
                    protocol_versions=[ProtocolVersionRecord(protocol="responses", version="1.0.0")],
                ),
            ),
            code=code,
        )

        created = project_client.agents.create_version_from_code(
            agent_name=agent_name,
            content=content,
            code_zip_sha256=zip_sha256,
        )
        print(f"Created hosted agent version: {created.version}")

        wait_for_agent_version_active(
            project_client=project_client,
            agent_name=agent_name,
            agent_version=created.version,
        )

        ensure_agent_identity_rbac(
            agent=created,
            credential=credential,
            subscription_id=subscription_id,
            foundry_project_endpoint=endpoint,
        )

        user_input = "Compute the shipping cost for a 3 kg package shipped domestically."
        print(f"User: {user_input}")
        response = hosted_openai_client.responses.create(input=user_input)

        response_text = response.output_text or ""
        print("Response:")
        print(response_text.encode("utf-8", errors="replace").decode("utf-8"))

        project_client.agents.delete_version(agent_name=agent_name, agent_version=created.version, force=True)
        print(f"Agent version {created.version} deleted")
        project_client.toolboxes.delete(TOOLBOX_NAME)
        print("Toolbox deleted")
        project_client.beta.skills.delete(SKILL_NAME)
        print("Skill deleted")


if __name__ == "__main__":
    main()
