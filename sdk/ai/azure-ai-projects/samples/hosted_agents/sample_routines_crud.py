# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to perform CRUD operations on Routines
    using the synchronous AIProjectClient.

    It creates a routine bound to an existing hosted agent, retrieves it,
    toggles its `enabled` state via `disable` / `enable`, lists routines,
    and finally deletes it. A `CustomRoutineTrigger` is used to keep the
    sample self-contained (no GitHub or schedule resources required).

    Routines are currently a preview feature. In the Python SDK, you access
    these operations via `project_client.beta.routines`.

USAGE:
    python sample_routines_crud.py

    Before running the sample:

    pip install "azure-ai-projects>=2.2.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) FOUNDRY_HOSTED_AGENT_NAME - The name of an existing Hosted Agent to invoke
       when the routine fires.
"""

import os

from dotenv import load_dotenv

from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    CustomRoutineTrigger,
    InvokeAgentResponsesApiRoutineAction,
    Routine,
    RoutineTrigger,
)

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
agent_name = os.environ["FOUNDRY_HOSTED_AGENT_NAME"]


def print_routine_state(routine: Routine) -> None:
    print(f"  - routine `{routine.name}` enabled={routine.enabled} description={routine.description!r}")


with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential, allow_preview=True) as project_client,
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
