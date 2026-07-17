# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to perform CRUD operations on Routines
    using the synchronous AIProjectClient.

    It uploads the basic hosted-agent code from `assets/basic-agent/` as a
    temporary hosted-agent version, creates a routine bound to that hosted
    agent, retrieves it, toggles its `enabled` state via `disable` / `enable`,
    lists routines, and finally deletes it. A `CustomRoutineTrigger` is used
    to keep the sample self-contained (no GitHub or schedule resources required).

    Routines are currently a preview feature. In the Python SDK, you access
    these operations via `project_client.beta.routines`.

USAGE:
    python sample_routines_crud.py

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

import os
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
    Routine,
    RoutineTrigger,
)

from hosted_agents_util import create_version_from_code, select_basic_agent_code_zip

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
agent_name = os.environ.get("FOUNDRY_HOSTED_AGENT_NAME", "MyHostedAgent")
model_name = os.environ["FOUNDRY_MODEL_NAME"]
dependency_resolution, code_zip_stream = select_basic_agent_code_zip(True)


def print_routine_state(routine: Routine) -> None:
    print(f"  - routine `{routine.name}` enabled={routine.enabled} description={routine.description!r}")


with (
    code_zip_stream as code_stream,
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    create_version_from_code(
        project_client=project_client,
        agent_name=agent_name,
        description="Routines CRUD hosted agent uploaded from assets/basic-agent.",
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

    routine_name = "sample-routine"

    try:
        project_client.beta.routines.delete(routine_name)
        print(f"Routine `{routine_name}` deleted")
    except ResourceNotFoundError:
        pass

    triggers: dict[str, RoutineTrigger] = {
        "manual": CustomRoutineTrigger(
            provider="sample-provider",
            event_name="sample-event",
            parameters={"source": "sample_routines_crud"},
        ),
    }

    action = InvokeAgentResponsesApiRoutineAction(agent_name=agent_name)

    created = project_client.beta.routines.create_or_update(
        routine_name,
        description="Routine created by the azure-ai-projects sample.",
        enabled=True,
        triggers=triggers,
        action=action,
    )
    print(f"Created routine: {created.name} enabled={created.enabled}")

    disabled = project_client.beta.routines.disable(routine_name)
    print(f"Disabled routine: {disabled.name} enabled={disabled.enabled}")

    fetched = project_client.beta.routines.get(routine_name)
    print("Retrieved routine after disable:")
    print_routine_state(fetched)

    enabled = project_client.beta.routines.enable(routine_name)
    print(f"Enabled routine: {enabled.name} enabled={enabled.enabled}")

    fetched = project_client.beta.routines.get(routine_name)
    print("Retrieved routine after enable:")
    print_routine_state(fetched)

    routines = list(project_client.beta.routines.list())
    print(f"Found {len(routines)} routine(s):")
    for item in routines:
        print(f"  - {item.name} enabled={item.enabled}")

    project_client.beta.routines.delete(routine_name)
    print("Routine deleted")
