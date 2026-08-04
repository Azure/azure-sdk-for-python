# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to create a Routine with a manual (custom)
    trigger and fire it on demand via `dispatch(...)`, then record the
    resulting run by polling `list_runs(...)` using the synchronous
    AIProjectClient.

    The sample uploads the basic hosted-agent code from `assets/basic-agent/`
    as a temporary hosted-agent version and routes the configured hosted agent
    name to that version. Because the trigger is a `CustomRoutineTrigger`, the
    routine never fires on its own; the sample explicitly invokes it with
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
    CustomRoutineTrigger,
    HostedAgentDefinition,
    InvokeAgentResponsesApiDispatchPayload,
    InvokeAgentResponsesApiRoutineAction,
    ProtocolVersionRecord,
    RoutineRun,
    RoutineRunPhase,
)

from hosted_agents_util import create_version_from_code, select_basic_agent_code_zip

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
agent_name = os.environ.get("FOUNDRY_HOSTED_AGENT_NAME", "MyHostedAgent")
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

    created = project_client.beta.routines.create_or_update(
        routine_name,
        description="Routine used by the dispatch sample.",
        enabled=True,
        triggers={
            "manual": CustomRoutineTrigger(
                provider="sample-provider",
                event_name="sample-event",
                parameters={},
            ),
        },
        action=InvokeAgentResponsesApiRoutineAction(agent_name=agent_name),
    )
    print(f"Created routine: {created.name} enabled={created.enabled}")

    dispatch_result = project_client.beta.routines.dispatch(
        routine_name,
        payload=InvokeAgentResponsesApiDispatchPayload(
            input="Say hello from a manually dispatched routine.",
        ),
    )
    print(f"Dispatched routine: dispatch_id={dispatch_result.dispatch_id} task_id={dispatch_result.task_id}")

    seen_phases: dict[str, RoutineRunPhase] = {}
    final_run: RoutineRun | None = None

    deadline = time.monotonic() + 180
    while time.monotonic() < deadline:
        runs = list(project_client.beta.routines.list_runs(routine_name, limit=20, order="desc"))
        for run in runs:
            if seen_phases.get(run.id) == run.phase:
                continue
            seen_phases[run.id] = run.phase  # type: ignore[assignment]
            print(
                f"  - run_id={run.id} phase={run.phase} status={run.status} "
                f"trigger_type={run.trigger_type} triggered_at={run.triggered_at} ended_at={run.ended_at}"
            )
            if str(run.status).lower() == "finished":
                final_run = run

        if final_run is not None:
            break
        time.sleep(5)

    if final_run:
        print("Final run:")
        print(json.dumps(final_run.as_dict(), indent=2, default=str))
        # Note: retrieving the response body produced by a routine-dispatched
        # run via `openai_client.responses.retrieve(final_run.response_id)` is
        # not yet supported by the service for this scenario.
    else:
        print("Dispatch did not produce a terminal run within the deadline.")

    project_client.beta.routines.delete(routine_name)
    print("Routine deleted")
