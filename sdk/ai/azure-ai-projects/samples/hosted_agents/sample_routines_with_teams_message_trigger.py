# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to create a Routine that fires when a new
    Microsoft Teams channel message arrives, then record the resulting runs by
    polling `list_runs(...)` using the synchronous AIProjectClient.

    The sample uploads the basic hosted-agent code from `assets/basic-agent/`
    as a temporary hosted-agent version, routes the configured hosted agent
    name to that version, and creates a routine configured with a
    `CustomRoutineTrigger`. The trigger uses a Teams-compatible custom
    connection and listens for the `on_new_channel_message` event on a specific
    Teams channel. After creating the routine, post a message to the configured
    channel to fire it. The sample polls the routine run history for a short
    period and then deletes the routine and hosted-agent version.

    Routines are currently a preview feature. In the Python SDK, you access
    these operations via `project_client.beta.routines`.

USAGE:
    python sample_routines_with_teams_message_trigger.py

    Before running the sample:

    pip install "azure-ai-projects>=2.3.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) FOUNDRY_MODEL_NAME - The deployment name of the AI model used by the
       temporary hosted agent.
    3) FOUNDRY_HOSTED_AGENT_NAME - Optional. The hosted agent name to route to
       the temporary uploaded version. Defaults to `MyHostedAgent`.
    4) TEAMS_CONNECTION_NAME - The Teams custom connection ID or name.
       Defaults to `teams-conn`.
    5) TEAMS_CHANNEL_URL - A Teams channel URL like the sample URL
       below. When set, the sample derives `groupId` and `channelId` from it.
    6) POLL_INTERVAL_SECONDS - Optional. Seconds to sleep between run-history polls.
        Defaults to 10.

    Sample channel:
    https://teams.microsoft.com/l/channel/<channel_id>/<channel_name>?groupId=<group_id>&tenantId=<tenant_id>
"""

import json
import os
import time
from urllib.parse import parse_qs, unquote, urlparse

from dotenv import load_dotenv

from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    CodeConfiguration,
    CustomRoutineTrigger,
    HostedAgentDefinition,
    InvokeAgentResponsesApiRoutineAction,
    ProtocolVersionRecord,
    RoutineRun,
)

from hosted_agents_util import create_version_from_code, select_basic_agent_code_zip


def parse_teams_channel_url(channel_url: str) -> tuple[str | None, str | None]:
    parsed = urlparse(channel_url)
    path_parts = [part for part in parsed.path.split("/") if part]

    channel_id = None
    if len(path_parts) >= 3 and path_parts[0] == "l" and path_parts[1] == "channel":
        channel_id = unquote(path_parts[2])

    query = parse_qs(parsed.query)
    group_id = query.get("groupId", [None])[0]
    return group_id, channel_id


load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
agent_name = os.environ.get("FOUNDRY_HOSTED_AGENT_NAME") or "MyHostedAgent"
model_name = os.environ["FOUNDRY_MODEL_NAME"]
teams_connection_name = os.environ.get("TEAMS_CONNECTION_NAME", "teams-conn")
teams_channel_url = os.environ["TEAMS_CHANNEL_URL"]
teams_group_id, teams_channel_id = parse_teams_channel_url(teams_channel_url)
poll_interval_seconds = int(os.environ.get("POLL_INTERVAL_SECONDS", "10"))
use_remote_build = os.environ.get("FOUNDRY_HOSTED_AGENT_REMOTE_BUILD", "true").strip().lower() == "true"
dependency_resolution, code_zip_stream = select_basic_agent_code_zip(True)


def main() -> None:
    with (
        code_zip_stream as code_stream,
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
        create_version_from_code(
            project_client=project_client,
            agent_name=agent_name,
            description="Teams channel routine sample hosted agent uploaded from assets/basic-agent.",
            definition=HostedAgentDefinition(
                cpu="0.5",
                memory="1Gi",
                code_configuration=CodeConfiguration(
                    runtime="python_3_14",
                    entry_point=["python", "main.py"],
                    dependency_resolution=dependency_resolution,
                ),
                environment_variables={
                    "FOUNDRY_PROJECT_ENDPOINT": endpoint,
                    "FOUNDRY_MODEL_NAME": model_name,
                },
                protocol_versions=[
                    ProtocolVersionRecord(protocol="responses", version="2.0.0"),
                    ProtocolVersionRecord(protocol="invocations", version="2.0.0"),
                ],
            ),
            metadata={"enableVnextExperience": "true"},
            code=code_stream,
        ),
    ):
        routine_name = "sample-routine-teams-channel-message"

        print(f"Preparing routine `{routine_name}` for Teams channel {teams_channel_id}.")
        print(f"Using Teams channel URL: {teams_channel_url}")
        print({"group_id": teams_group_id, "channel_id": teams_channel_id})
        try:
            print(f"Deleting any existing routine `{routine_name}`.")
            project_client.beta.routines.delete(routine_name)
            print(f"Routine `{routine_name}` deleted")
        except ResourceNotFoundError:
            pass

        print(f"Creating routine `{routine_name}`.")
        created = project_client.beta.routines.create_or_update(
            routine_name,
            description="Routine used by the Teams channel message trigger sample.",
            enabled=True,
            triggers={
                "incoming": CustomRoutineTrigger(
                    provider="teams",
                    event_name="on_new_channel_message",
                    parameters={
                        "connection_id": teams_connection_name,
                        "thread_type": "channel",
                        "group_id": teams_group_id,
                        "channel_id": teams_channel_id,
                    },
                )
            },
            action=InvokeAgentResponsesApiRoutineAction(agent_name=agent_name),
        )
        print(
            f"Created routine: {created.name} enabled={created.enabled} "
            f"provider=teams event_name=on_new_channel_message group_id={teams_group_id}"
        )
        print("Post a new message to the configured Teams channel to fire the routine.")
        print("Waiting for a routine run for up to 10 minutes...")

        try:
            seen_phases: dict[str, str] = {}
            final_run: RoutineRun | None = None
            run_was_triggered = False
            terminal_statuses = {"finished", "failed", "killed"}

            deadline = time.monotonic() + 600
            while deadline > time.monotonic():
                runs = list(project_client.beta.routines.list_runs(routine_name, limit=20, order="desc"))
                for run in runs:
                    run_was_triggered = True
                    current_phase = str(run.phase)
                    if seen_phases.get(run.id) == current_phase:
                        continue
                    seen_phases[run.id] = current_phase
                    print(
                        f"  - run_id={run.id} phase={run.phase} status={run.status} "
                        f"trigger_type={run.trigger_type} triggered_at={run.triggered_at} ended_at={run.ended_at}"
                    )
                    if str(run.status).lower() in terminal_statuses:
                        final_run = run

                if final_run is not None:
                    break
                time.sleep(poll_interval_seconds)

            if final_run:
                print("Final run:")
                print(json.dumps(final_run.as_dict(), indent=2, default=str))
                print(f"The response Id is {final_run.response_id}")
            elif run_was_triggered:
                print("A routine run was observed, but no terminal run state was reached within the deadline.")
            else:
                print("No Teams-triggered run was observed within the deadline.")
        except KeyboardInterrupt:
            print("Interrupted by user; cleaning up routine before exiting.")
        finally:
            try:
                project_client.beta.routines.delete(routine_name)
                print("Routine deleted")
            except ResourceNotFoundError:
                pass


if __name__ == "__main__":
    main()
