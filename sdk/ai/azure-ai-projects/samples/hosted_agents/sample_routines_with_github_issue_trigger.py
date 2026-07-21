# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to create a Routine that fires when a GitHub
    issue is opened in a GitHub repository.

    The sample first uploads the basic hosted-agent code from
    `samples/hosted_agents/assets/basic-agent/` as a temporary hosted-agent
    version, routes the configured hosted agent name to that version, and then
    creates a routine configured with a `GitHubIssueRoutineTrigger`. The trigger
    uses a GitHub-compatible Foundry RemoteTool connection supplied through
    `GITHUB_CONNECTION_NAME`. After creating the routine, open an issue in the
    configured repository to fire it. The sample polls the routine run history
    for a short period and then deletes the routine and hosted-agent version.

    Routines are currently a preview feature. In the Python SDK, you access
    these operations via `project_client.beta.routines`.

USAGE:
    python sample_routines_with_github_issue_trigger.py

    Before running the sample:

    pip install "azure-ai-projects>=2.3.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) FOUNDRY_MODEL_NAME - The deployment name of the AI model used by the
       temporary hosted agent.
    3) FOUNDRY_HOSTED_AGENT_NAME - Optional. The hosted agent name to route to
       the temporary uploaded version. Defaults to `MyHostedAgent`.
    4) GITHUB_CONNECTION_NAME - The Foundry GitHub RemoteTool connection name.
       The connection must be GitHub-compatible and use PAT or OAuth2 credentials.
    5) GITHUB_USERNAME - The GitHub owner or organization name.
    6) GITHUB_REPOSITORY - The GitHub repository name in the format of https://github.com/xxx/xxx.git.
    7) POLL_INTERVAL_SECONDS - Optional. Seconds to sleep between run-history polls.
        Defaults to 10.
"""

import json
import os
import time

from dotenv import load_dotenv

from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    CodeConfiguration,
    GitHubIssueEvent,
    GitHubIssueRoutineTrigger,
    HostedAgentDefinition,
    InvokeAgentResponsesApiRoutineAction,
    ProtocolVersionRecord,
    RoutineRun,
)

from hosted_agents_util import create_version_from_code, select_basic_agent_code_zip

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
agent_name = os.environ.get("FOUNDRY_HOSTED_AGENT_NAME", "MyHostedAgent")
model_name = os.environ["FOUNDRY_MODEL_NAME"]
github_connection_name = os.environ["GITHUB_CONNECTION_NAME"]
poll_interval_seconds = int(os.environ.get("POLL_INTERVAL_SECONDS", "10"))

github_owner = os.environ["GITHUB_USERNAME"]
github_repository = os.environ["GITHUB_REPOSITORY"]


def main() -> None:
    dependency_resolution, code_zip_stream = select_basic_agent_code_zip(True)

    with (
        code_zip_stream as code_stream,
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
        create_version_from_code(
            project_client=project_client,
            agent_name=agent_name,
            description="GitHub issue routine sample hosted agent uploaded from assets/basic-agent.",
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
                protocol_versions=[ProtocolVersionRecord(protocol="responses", version="2.0.0")],
            ),
            code=code_stream,
        ),
    ):
        routine_name = "sample-routine-github-issue"

        print(f"Preparing routine `{routine_name}` for {github_repository}.")
        try:
            print(f"Deleting any existing routine `{routine_name}`.")
            project_client.beta.routines.delete(routine_name)
            print(f"Routine `{routine_name}` deleted")
        except ResourceNotFoundError:
            pass

        print(f"Creating routine `{routine_name}`.")
        created = project_client.beta.routines.create_or_update(
            routine_name,
            description="Routine used by the GitHub issue trigger sample.",
            enabled=True,
            triggers={
                "on-issue": GitHubIssueRoutineTrigger(
                    connection_id=github_connection_name,  # Currently accepts a connection name.
                    owner=github_owner,
                    repository=github_repository,
                    issue_event=GitHubIssueEvent.OPENED,
                ),
            },
            action=InvokeAgentResponsesApiRoutineAction(agent_name=agent_name),
        )
        print(
            f"Created routine: {created.name} enabled={created.enabled} "
            f"repo={github_owner}/{github_repository} event={GitHubIssueEvent.OPENED}"
        )
        print(f"Open a GitHub issue in {github_repository} to fire the routine.")
        print("Waiting for a routine run for up to 10 minutes...")

        try:
            seen_phases: dict[str, str] = {}
            final_run: RoutineRun | None = None
            run_was_triggered = False
            terminal_statuses = {"finished", "failed", "killed"}

            deadline = time.monotonic() + 600
            while time.monotonic() < deadline:
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
                print("No GitHub issue-triggered run was observed within the deadline.")
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
