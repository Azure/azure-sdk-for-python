# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Create a shipping-cost Skill and a Toolbox version that exposes it over a
    Foundry Toolbox MCP endpoint, then upload ``assets/toolbox-agent/`` as a
    REMOTE_BUILD code asset for a Hosted Agent version. The sample waits for
    the new version to become active, assigns Azure AI User RBAC to the hosted
    agent identity on the Foundry account, temporarily routes the Hosted Agent
    endpoint to that version, sends a query through the Responses API, and
    finally restores the previous endpoint and deletes the temporary agent
    version, toolbox, and skill.

USAGE:
    python sample_toolbox_with_skill.py

    Before running the sample:

    pip install "azure-ai-projects>=2.3.0" azure-identity azure-mgmt-authorization azure-mgmt-resource python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the
       Overview page of your Microsoft Foundry portal.
    2) FOUNDRY_MODEL_NAME - The deployment name of the AI model, as found under
       the "Name" column in the "Models + endpoints" tab in your Foundry project.
    3) FOUNDRY_HOSTED_AGENT_NAME - Optional. The Hosted Agent name. Defaults to
        `MyHostedAgent`. The Hosted Agent must already exist.
    4) AZURE_SUBSCRIPTION_ID - The Azure subscription ID containing the
        Foundry project/account. This is used to assign Azure AI User RBAC to
        the hosted agent identity.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    CodeConfiguration,
    CodeDependencyResolution,
    HostedAgentDefinition,
    ProtocolVersionRecord,
)

from hosted_agents_util import create_version_from_code
from rbac_util import ensure_agent_identity_rbac
from util import zip_directory

from azure.core.exceptions import ResourceNotFoundError
from azure.ai.projects.models import (
    SkillInlineContent,
    ToolSearchToolboxTool,
    ToolboxSkillReference,
)

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
model_name = os.environ["FOUNDRY_MODEL_NAME"]
subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
agent_name = os.environ.get("FOUNDRY_HOSTED_AGENT_NAME", "MyHostedAgent")

_HOSTED_AGENT_SOURCE_DIR = Path(__file__).parent / "assets" / "toolbox-agent"

SKILL_NAME = "shipping-cost-skill"
TOOLBOX_NAME = "toolbox_with_skill"


def main() -> None:
    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
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
            tools=[ToolSearchToolboxTool()],
            skills=[ToolboxSkillReference(name=skill_version.name, version=skill_version.version)],
        )
        print(f"Created toolbox: {toolbox_version.name} version={toolbox_version.version}")

        toolbox_mcp_url = f"{endpoint}/toolboxes/{TOOLBOX_NAME}/versions/{toolbox_version.version}/mcp?api-version=v1"

        zip_filename = "hosted-toolbox-agent.zip"
        _, _, zip_path = zip_directory(_HOSTED_AGENT_SOURCE_DIR, zip_filename)

        try:
            with (
                zip_path.open("rb") as code_stream,
                create_version_from_code(
                    project_client=project_client,
                    agent_name=agent_name,
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
                        protocol_versions=[ProtocolVersionRecord(protocol="responses", version="2.0.0")],
                    ),
                    code=code_stream,
                ) as agent,
                project_client.get_openai_client(agent_name=agent_name) as hosted_openai_client,
            ):

                # toolbox requires the hosted agent identity to have Foundry User RBAC on the Foundry account, so assign it here
                ensure_agent_identity_rbac(
                    agent=agent,
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
        finally:
            project_client.toolboxes.delete(TOOLBOX_NAME)
            print("Toolbox deleted")
            project_client.beta.skills.delete(SKILL_NAME)
            print("Skill deleted")


if __name__ == "__main__":
    main()
