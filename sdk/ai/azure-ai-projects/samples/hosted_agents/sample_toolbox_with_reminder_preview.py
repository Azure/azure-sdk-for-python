# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Create a Toolbox version that exposes a Reminder Preview tool over a
    Foundry Toolbox MCP endpoint, then upload ``assets/toolbox-agent/`` as a
    REMOTE_BUILD code asset for a Hosted Agent version. The sample waits for
    the new version to become active, assigns Azure AI User RBAC to the hosted
    agent identity on the Foundry account, temporarily routes the Hosted Agent
    endpoint to that version, sends a reminder request through the Responses
    API, queries routines to find the service-created one-shot routine, and
    finally restores the previous endpoint and deletes the temporary agent
    version and toolbox.

    The hosted agent must already exist; create it first with:
        samples/hosted_agents/sample_create_hosted_agent_from_image.py

USAGE:
    python sample_toolbox_with_reminder_preview.py

    Before running the sample:

    pip install "azure-ai-projects>=2.3.0" azure-identity azure-mgmt-authorization azure-mgmt-resource python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the
       Overview page of your Microsoft Foundry portal.
    2) FOUNDRY_MODEL_NAME - The deployment name of the AI model.
    3) FOUNDRY_HOSTED_AGENT_NAME - Optional. The Hosted Agent name. Defaults to
       `MyHostedAgent`. The Hosted Agent must already exist.
    4) AZURE_SUBSCRIPTION_ID - The Azure subscription ID containing the
        Foundry project/account. This is used to assign Azure AI User RBAC to
        the hosted agent identity.
"""

import os
import time
from pathlib import Path

from dotenv import load_dotenv

from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    CodeConfiguration,
    CodeDependencyResolution,
    HostedAgentDefinition,
    ProtocolVersionRecord,
    ReminderPreviewToolboxTool,
)

from hosted_agents_util import create_version_from_code
from rbac_util import ensure_agent_identity_rbac
from util import zip_directory

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
model_name = os.environ["FOUNDRY_MODEL_NAME"]
subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
agent_name = os.environ.get("FOUNDRY_HOSTED_AGENT_NAME", "MyHostedAgent")

_HOSTED_AGENT_SOURCE_DIR = Path(__file__).parent / "assets" / "toolbox-agent"


TOOLBOX_NAME = "toolbox_with_reminder_preview"


def list_routine_names(project_client: AIProjectClient) -> set[str]:
    routines = list(project_client.beta.routines.list())
    return {routine.name for routine in routines if routine.name}


def main() -> None:
    created_routine_names: set[str] = set()
    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    ):
        try:
            project_client.toolboxes.delete(TOOLBOX_NAME)
        except ResourceNotFoundError:
            pass

        toolbox_version = project_client.toolboxes.create_version(
            name=TOOLBOX_NAME,
            description="Toolbox exposing a reminder preview tool.",
            tools=[
                ReminderPreviewToolboxTool(
                    name="reminder",
                    description="Schedule a reminder to re-invoke the agent after a short delay.",
                ),
            ],
            metadata={"enableVnextExperience": "true"},
        )
        print(f"Created toolbox: {toolbox_version.name} version={toolbox_version.version}")

        toolbox_mcp_url = f"{endpoint}/toolboxes/{TOOLBOX_NAME}/versions/{toolbox_version.version}/mcp?api-version=v1"

        zip_filename = "hosted-toolbox-mcp-reminder-preview-agent.zip"
        _, _, zip_path = zip_directory(_HOSTED_AGENT_SOURCE_DIR, zip_filename)
        try:
            with (
                zip_path.open("rb") as code_stream,
                create_version_from_code(
                    project_client=project_client,
                    agent_name=agent_name,
                    description="Hosted agent code for toolbox MCP reminder preview tool.",
                    definition=HostedAgentDefinition(
                        cpu="0.5",
                        memory="1Gi",
                        code_configuration=CodeConfiguration(
                            runtime="python_3_13",
                            entry_point=["python", "main.py"],
                            dependency_resolution=CodeDependencyResolution.REMOTE_BUILD,
                        ),
                        environment_variables={
                            "FOUNDRY_PROJECT_ENDPOINT": endpoint,
                            "FOUNDRY_MODEL_NAME": model_name,
                            "MCP_SERVER_URL": toolbox_mcp_url,
                        },
                        protocol_versions=[
                            ProtocolVersionRecord(protocol="responses", version="2.0.0"),
                            ProtocolVersionRecord(protocol="invocations", version="2.0.0"),
                        ],
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

                routines_before = list_routine_names(project_client)

                user_input = "Use the reminder tool to remind me in 1 minute to check the coffee."
                print(f"User: {user_input}")
                response = hosted_openai_client.responses.create(
                    input=user_input,
                )

                response_text = response.output_text or ""
                print("Response:")
                print(response_text.encode("utf-8", errors="replace").decode("utf-8"))

                print("Routines after scheduling the reminder:")
                deadline = time.monotonic() + 30
                while time.monotonic() < deadline:
                    routines_after = list_routine_names(project_client)
                    created_routine_names = routines_after - routines_before
                    if created_routine_names:
                        break
                    print("No new routine found yet; checking again shortly...")
                    time.sleep(5)

                if created_routine_names:
                    print("Retrieved new routine details:")
                    for routine_name in sorted(created_routine_names):
                        routine = project_client.beta.routines.get(routine_name)
                        print(f"  - {routine.name} enabled={routine.enabled} description={routine.description!r}")
                else:
                    print(
                        "No new routine was visible in project_client.beta.routines.list() after scheduling the reminder."
                    )
        finally:
            project_client.toolboxes.delete(TOOLBOX_NAME)
            print("Toolbox deleted")


if __name__ == "__main__":
    main()
