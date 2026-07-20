# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Demonstrates deploying a code-based Hosted Agent that discovers and uses a
    Reminder Preview tool from a Foundry Toolbox MCP endpoint via Agent Framework.

    The sample:
        1. Creates a toolbox version that contains ``ReminderPreviewToolboxTool``.
        2. Uploads the checked-in ``assets/hosted-agent-sample5-toolbox-tip.zip``
          code asset copied from Microsoft Foundry.
    3. Deploys a new Hosted Agent version, forwarding the project endpoint,
          model name, and toolbox MCP URL to the hosted agent code.
    4. Waits for the version to become active.
        5. Sends a reminder request to the hosted agent via the Responses API.
    6. Queries routines to find and retrieve the service-created one-shot routine.
    7. Cleans up created resources (agent version, toolbox, conversation, and routine).

    The hosted agent must already exist; create it first with:
        samples/hosted_agents/sample_create_hosted_agent_from_image.py

USAGE:
    python sample_toolbox_with_reminder_preview.py

    Before running the sample:

    pip install "azure-ai-projects>=2.3.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the
       Overview page of your Microsoft Foundry portal.
    2) FOUNDRY_MODEL_NAME - The deployment name of the AI model.
    3) FOUNDRY_HOSTED_AGENT_NAME - Optional. The Hosted Agent name. Defaults to
       `MyHostedAgent`. The Hosted Agent must already exist.
"""

import os
import sys
import time
from pathlib import Path

_SAMPLES_DIR = Path(__file__).resolve().parents[1]
if str(_SAMPLES_DIR) not in sys.path:
    sys.path.insert(0, str(_SAMPLES_DIR))

from dotenv import load_dotenv

from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    AgentEndpointConfig,
    CodeConfiguration,
    CodeDependencyResolution,
    FixedRatioVersionSelectionRule,
    HostedAgentDefinition,
    ProtocolConfiguration,
    ProtocolVersionRecord,
    ReminderPreviewToolboxTool,
    ResponsesProtocolConfiguration,
    VersionSelector,
)

from hosted_agents_util import wait_for_agent_version_active
from util import zip_directory

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
model_name = os.environ["FOUNDRY_MODEL_NAME"]
agent_name = os.environ.get("FOUNDRY_HOSTED_AGENT_NAME", "MyHostedAgent")

_HOSTED_AGENT_SOURCE_DIR = Path(__file__).parent / "assets" / "toolbox-agent"


TOOLBOX_NAME = "toolbox_with_reminder_preview"


def list_routine_names(project_client: AIProjectClient) -> set[str]:
    routines = list(project_client.beta.routines.list())
    print(f"Found {len(routines)} routines")
    for routine in routines:
        print(f"  - {routine.name} enabled={routine.enabled}")
    return {routine.name for routine in routines if routine.name}


def main() -> None:
    created_routine_names: set[str] = set()
    session_id: str | None = None

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
        )
        print(f"Created toolbox: {toolbox_version.name} version={toolbox_version.version}")

        toolbox_mcp_url = f"{endpoint}/toolboxes/{TOOLBOX_NAME}/versions/{toolbox_version.version}/mcp?api-version=v1"

        zip_filename = "hosted-toolbox-mcp-reminder-preview-agent.zip"
        _, _, zip_path = zip_directory(_HOSTED_AGENT_SOURCE_DIR, zip_filename)
        with zip_path.open("rb") as code_stream:
            created = project_client.agents.create_version_from_code(
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
                        "AGENT_NAME": "hosted-toolbox-mcp-reminder-preview",
                        "AGENT_STORE_RESPONSES": "true",
                        "AGENT_INSTRUCTIONS": (
                            "You are a helpful assistant that can schedule reminders. "
                            "When the user asks for a reminder, use the reminder tool from the toolbox."
                        ),
                    },
                    protocol_versions=[
                        ProtocolVersionRecord(protocol="responses", version="2.0.0"),
                        ProtocolVersionRecord(protocol="invocations", version="2.0.0"),
                    ],
                ),
                code=code_stream,
            )
        print(f"Created hosted agent version: {created.version}")

        wait_for_agent_version_active(
            project_client=project_client,
            agent_name=agent_name,
            agent_version=created.version,
        )

        original_agent_endpoint = project_client.agents.get(agent_name).agent_endpoint
        endpoint_config = AgentEndpointConfig(
            version_selector=VersionSelector(
                version_selection_rules=[
                    FixedRatioVersionSelectionRule(agent_version=created.version, traffic_percentage=100),
                ]
            ),
            protocol_configuration=ProtocolConfiguration(responses=ResponsesProtocolConfiguration()),
        )
        project_client.agents.update_details(agent_name=agent_name, agent_endpoint=endpoint_config)
        print(f"Agent endpoint configured for version {created.version}")

        print("Routines before scheduling the reminder:")
        routines_before = list_routine_names(project_client)

        with project_client.get_openai_client(agent_name=agent_name) as hosted_openai_client:
            conversation = hosted_openai_client.conversations.create()
            conversation_id = conversation.id
            print(f"Created conversation: {conversation_id}")

            user_input = "Use the reminder tool to remind me in 1 minute to check the coffee."
            print(f"User: {user_input}")
            response = hosted_openai_client.responses.create(
                conversation=conversation_id,
                input=user_input,
            )

            if conversation_id:
                hosted_openai_client.conversations.delete(conversation_id=conversation_id)
                print("Conversation deleted")

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
            print("No new routine was visible in project_client.beta.routines.list() after scheduling the reminder.")

        project_client.agents.update_details(agent_name=agent_name, agent_endpoint=original_agent_endpoint)
        print("Agent endpoint restored")
        project_client.agents.delete_version(agent_name=agent_name, agent_version=created.version, force=True)
        print(f"Agent version {created.version} deleted")

        if session_id:
            project_client.agents.delete_session(agent_name=agent_name, session_id=session_id)
            print(f"Session {session_id} deleted")
            session_id = None

        for routine_name in sorted(created_routine_names):
            project_client.beta.routines.delete(routine_name)
            print(f"Routine `{routine_name}` deleted")

        project_client.toolboxes.delete(TOOLBOX_NAME)
        print("Toolbox deleted")


if __name__ == "__main__":
    main()
