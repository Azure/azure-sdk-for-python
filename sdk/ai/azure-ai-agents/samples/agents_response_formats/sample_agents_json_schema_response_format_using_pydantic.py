# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use agents with JSON schema output format.
    It uses the Pydantic package to define the output JSON schema from Python classes.

USAGE:
    python sample_agents_json_schema_response_format_using_pydantic.py

    Before running the sample:

    pip install azure-ai-projects azure-ai-agents azure-identity pydantic

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
                          page of your Azure AI Foundry portal.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
"""

import os

from enum import Enum
from pydantic import BaseModel, TypeAdapter
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import (
    ListSortOrder,
    MessageRole,
    ResponseFormatJsonSchema,
    ResponseFormatJsonSchemaType,
    RunStatus,
)


# Create the pydantic model to represent the planet names and there masses.
class PlanetName(str, Enum):
    Mercury = "Mercury"
    Venus = "Venus"
    Earth = "Earth"
    Mars = "Mars"
    Jupiter = "Jupiter"
    Saturn = "Saturn"
    Uranus = "Uranus"
    Neptune = "Neptune"


class Planet(BaseModel):
    name: PlanetName
    mass: float


class Planets(BaseModel):
    planets: list[Planet]


project_client = AIProjectClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

with project_client:
    agents_client = project_client.agents

    agent = agents_client.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="my-agent",
        instructions="You are helpful agent. Your response is JSON formatted.",
        response_format=ResponseFormatJsonSchemaType(
            json_schema=ResponseFormatJsonSchema(
                name="planet_mass",
                description="Masses of Solar System planets.",
                schema=Planets.model_json_schema(),
            )
        ),
    )
    print(f"Created agent, agent ID: {agent.id}")

    thread = agents_client.threads.create()
    print(f"Created thread, thread ID: {thread.id}")

    message = agents_client.messages.create(
        thread_id=thread.id,
        role="user",
        content="Hello, give me a list of planets in our solar system, and their mass in kilograms.",
    )
    print(f"Created message, message ID: {message.id}")

    run = agents_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)

    if run.status != RunStatus.COMPLETED:
        print(f"The run did not succeed: {run.status=}.")

    agents_client.delete_agent(agent.id)
    print("Deleted agent")

    messages = agents_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
    for msg in messages:
        if msg.text_messages:
            last_text = msg.text_messages[-1]
            print(f"{msg.role}: {last_text.text.value}")
            # Deserialize the Agent's JSON response to the `Planets` class defined above
            if msg.role == MessageRole.AGENT:
                planets = TypeAdapter(Planets).validate_json(last_text.text.value)
                for planet in planets.planets:
                    print(f"The mass of {planet.name.value} is {planet.mass} kg.")
