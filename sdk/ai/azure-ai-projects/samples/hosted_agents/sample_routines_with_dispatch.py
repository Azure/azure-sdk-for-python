# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to create a Routine with a timer scheduled
    far in the future, fire it early via `dispatch(...)`, then record the
    resulting run by polling `list_runs(...)` using the synchronous
    AIProjectClient.

    The sample uploads the basic hosted-agent code from `assets/basic-agent/`
    as a temporary hosted-agent version and routes the configured hosted agent
    name to that version. The timer is scheduled beyond the sample's polling
    window, and the sample explicitly invokes the routine early with
    `project_client.beta.routines.dispatch(...)` passing an
    `InvokeAgentResponsesApiDispatchPayload` carrying the input sent to the
    agent. The sample then polls the run history until a terminal phase is
    reached (or a deadline elapses), printing each observed transition. The
    routine and hosted-agent version are deleted at the end of the sample.

    Routines are currently a preview feature. In the Python SDK, you access
    these operations via `project_client.beta.routines`.

USAGE:
    python sample_routines_with_dispatch.py

    Before running the sample:

    pip install "azure-ai-projects>=2.2.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) FOUNDRY_MODEL_NAME - The deployment name of the AI model used by the
       temporary hosted agent.
    3) FOUNDRY_HOSTED_AGENT_NAME - Optional. The Hosted Agent name. Defaults to
       `MyHostedAgent`.
"""

import datetime
import json
import os
import time

from dotenv import load_dotenv

from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    CodeConfiguration,
    CodeDependencyResolution,
    HostedAgentDefinition,
    InvokeAgentResponsesApiDispatchPayload,
    InvokeAgentResponsesApiRoutineAction,
    ProtocolVersionRecord,
    RoutineRun,
    RoutineRunPhase,
    TimerRoutineTrigger,
)

from hosted_agents_util import create_version_from_code, select_basic_agent_code_zip

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
agent_name = os.environ.get("FOUNDRY_HOSTED_AGENT_NAME") or "MyHostedAgent"
model_name = os.environ["FOUNDRY_MODEL_NAME"]
dependency_resolution, code_zip_stream = select_basic_agent_code_zip(True)


with (
    code_zip_stream as code_stream,
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    create_version_from_code(
        project_client=project_client,
        agent_name=agent_name,
        description="Routines dispatch hosted agent uploaded from assets/basic-agent.",
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
            },
            protocol_versions=[ProtocolVersionRecord(protocol="responses", version="2.0.0")],
        ),
        code=code_stream,
    ),
):

    routine_name = "sample-routine-dispatch"

    try:
        project_client.beta.routines.delete(routine_name)
        print(f"Routine `{routine_name}` deleted")
    except ResourceNotFoundError:
        pass

    fire_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
    created = project_client.beta.routines.create_or_update(
        routine_name,
        description="Long-timer routine dispatched before its scheduled fire time.",
        enabled=True,
        triggers={"once": TimerRoutineTrigger(at=fire_at)},
        action=InvokeAgentResponsesApiRoutineAction(agent_name=agent_name),
    )
    print(f"Created routine: {created.name} enabled={created.enabled} fire_at={fire_at.isoformat()}")

    dispatch_result = project_client.beta.routines.dispatch(
        routine_name,
        payload=InvokeAgentResponsesApiDispatchPayload(
            input="Say hello from a timer routine dispatched before its scheduled fire time.",
        ),
    )
    print(f"Dispatched routine: dispatch_id={dispatch_result.dispatch_id} task_id={dispatch_result.task_id}")

    final_run: RoutineRun | None = None
    deadline = time.monotonic() + 180
    while time.monotonic() < deadline:
        final_run = next(
            (
                run
                for run in project_client.beta.routines.list_runs(routine_name, limit=20, order="desc")
                if run.dispatch_id == dispatch_result.dispatch_id
                and run.phase in (RoutineRunPhase.COMPLETED, RoutineRunPhase.FAILED)
            ),
            None,
        )
        if final_run is not None:
            break
        time.sleep(5)

    if final_run:
        print("Final run:")
        print(json.dumps(final_run.as_dict(), indent=2, default=str))
        if final_run.triggered_at is not None:
            scheduled_local = fire_at.astimezone()
            triggered_local = final_run.triggered_at.astimezone()
            print(
                f"Routine was scheduled to trigger around {scheduled_local:%H:%M:%S}, "
                f"but dispatch caused it to trigger at {triggered_local:%H:%M:%S}."
            )
    else:
        print("Dispatch did not produce a terminal run within the deadline.")

    project_client.beta.routines.delete(routine_name)
    print("Routine deleted")
