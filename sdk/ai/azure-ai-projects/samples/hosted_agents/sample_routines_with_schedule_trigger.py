# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to create a Routine that fires on a
    recurring cron schedule, then record the resulting runs by polling
    `list_runs(...)` using the synchronous AIProjectClient.

    The sample uploads the basic hosted-agent code from `assets/basic-agent/`
    as a temporary hosted-agent version, routes the configured hosted agent
    name to that version, and schedules the routine with a
    `ScheduleRoutineTrigger` using a 5-field cron expression. The service
    enforces a minimum interval of five minutes, so the sample polls the
    run history for up to ~6 minutes to catch the first fire, prints each
    observed phase transition, then deletes the routine and hosted-agent
    version.

    Routines are currently a preview feature. In the Python SDK, you access
    these operations via `project_client.beta.routines`.

USAGE:
    python sample_routines_with_schedule_trigger.py

    Before running the sample:

    pip install "azure-ai-projects>=2.2.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) FOUNDRY_MODEL_NAME - The deployment name of the AI model used by the
        temporary hosted agent.
    3) FOUNDRY_HOSTED_AGENT_NAME - Optional. The Hosted Agent name. Defaults to
        `MyHostedAgent`.
    4) POLL_INTERVAL_SECONDS - Optional. Seconds to sleep between run-history polls.
    Defaults to 15.
"""

import json
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    CodeConfiguration,
    HostedAgentDefinition,
    InvokeAgentResponsesApiRoutineAction,
    ProtocolVersionRecord,
    RoutineRun,
    RoutineRunPhase,
    ScheduleRoutineTrigger,
)

_HOSTED_AGENTS_DIR = Path(__file__).resolve().parent
if str(_HOSTED_AGENTS_DIR) not in sys.path:
    sys.path.insert(0, str(_HOSTED_AGENTS_DIR))

from hosted_agents_util import create_version_from_code, select_basic_agent_code_zip

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
agent_name = os.environ.get("FOUNDRY_HOSTED_AGENT_NAME", "MyHostedAgent")
model_name = os.environ["FOUNDRY_MODEL_NAME"]
poll_interval_seconds = int(os.environ.get("POLL_INTERVAL_SECONDS", "15"))
dependency_resolution, code_zip_stream = select_basic_agent_code_zip(True)


def main() -> None:
    with (
        code_zip_stream as code_stream,
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
        create_version_from_code(
            project_client=project_client,
            agent_name=agent_name,
            description="Routines schedule hosted agent uploaded from assets/basic-agent.",
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
        routine_name = "sample-routine-schedule"

        try:
            project_client.beta.routines.delete(routine_name)
            print(f"Routine `{routine_name}` deleted")
        except ResourceNotFoundError:
            pass

        # Fire every 5 minutes (the service-enforced minimum interval) in UTC.
        cron_expression = "*/5 * * * *"
        time_zone = "UTC"
        created = project_client.beta.routines.create_or_update(
            routine_name,
            description="Routine used by the schedule-trigger sample.",
            enabled=True,
            triggers={
                "every_five_minutes": ScheduleRoutineTrigger(
                    cron_expression=cron_expression,
                    time_zone=time_zone,
                )
            },
            action=InvokeAgentResponsesApiRoutineAction(agent_name=agent_name),
        )
        print(
            f"Created routine: {created.name} enabled={created.enabled} "
            f"cron={cron_expression!r} time_zone={time_zone!r}"
        )

        try:
            terminal_phases = {RoutineRunPhase.COMPLETED, RoutineRunPhase.FAILED}
            seen_phases: dict[str, str] = {}
            final_run: RoutineRun | None = None

            # Poll for up to ~6m30s to catch the first scheduled fire.
            max_polls = max(1, (6 * 60 + 30) // poll_interval_seconds + 1)
            print(
                f"Poll `{routine_name}` every {poll_interval_seconds}s for new runs "
                f"(up to {max_polls} iterations, ~6m30s).",
                end="",
                flush=True,
            )
            dots_pending = False
            for _ in range(max_polls):
                runs = list(project_client.beta.routines.list_runs(routine_name, limit=20, order="desc"))
                for run in runs:
                    if seen_phases.get(run.id) == run.phase:
                        continue
                    seen_phases[run.id] = str(run.phase)
                    if dots_pending:
                        print()
                        dots_pending = False
                    print(
                        f"  - run_id={run.id} phase={run.phase} status={run.status} "
                        f"trigger_type={run.trigger_type} triggered_at={run.triggered_at} ended_at={run.ended_at}"
                    )
                    if str(run.status).lower() == "finished":
                        final_run = run

                if final_run is not None:
                    break
                time.sleep(poll_interval_seconds)
                print(".", end="", flush=True)
                dots_pending = True

            if dots_pending:
                print()

            if final_run:
                print("Final run:")
                print(json.dumps(final_run.as_dict(), indent=2, default=str))
                # Note: retrieving the response body produced by a routine-dispatched
                # run via `openai_client.responses.retrieve(final_run.response_id)` is
                # not yet supported by the service for this scenario.
            else:
                print("Schedule did not produce a terminal run within the deadline.")
        except KeyboardInterrupt:
            print("Interrupted by user; cleaning up routine before exiting.")
        finally:
            # Always delete the routine so it stops firing on the schedule,
            # even if the sample was interrupted or raised an exception.
            try:
                project_client.beta.routines.delete(routine_name)
                print("Routine deleted")
            except ResourceNotFoundError:
                pass


if __name__ == "__main__":
    main()
