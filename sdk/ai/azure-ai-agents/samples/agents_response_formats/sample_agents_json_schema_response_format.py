# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use agents with JSON schema output format.

USAGE:
    python sample_agents_json_schema_response_format.py

    Before running the sample:

    pip install azure-ai-projects azure-ai-agents azure-identity

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
                          page of your Azure AI Foundry portal.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
"""

import os
import json
from typing import Dict, Any
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import (
    ListSortOrder,
    MessageRole,
    ResponseFormatJsonSchema,
    ResponseFormatJsonSchemaType,
    RunStatus,
)

# Defines a JSON schema for listing Solar System planets and their masses. We would like the AI model to respond in this format.
# See `sample_agents_json_schema_response_format_using_pydantic.py` for an alternative way to define the schema using Pydantic.
json_schema: Dict[str, Any] = {
    "$defs": {
        "PlanetName": {
            "type": "string",
            "description": "The name of the planet",
            "enum": ["Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"],
        }
    },
    "type": "object",
    "description": "Information about the planets in the Solar System",
    "properties": {
        "planets": {
            "type": "array",
            "items": {
                "type": "object",
                "description": "Information about a planet in the Solar System",
                "properties": {
                    "name": {"$ref": "#/$defs/PlanetName"},
                    "mass": {
                        "type": "number",
                        "description": "Mass of the planet in kilograms",
                    },
                    "relative_mass": {
                        "type": "number",
                        "description": "Relative mass of the planet compared to Earth (for example, a value of 2.0 means the planet is twice as massive as Earth)",
                    },
                },
                "required": ["name", "mass"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["planets"],
    "additionalProperties": False,
}


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
                description="Masses of Solar System planets",
                schema=json_schema,
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
            # Convert the Agent's JSON response message to a Dict object, extract and print planet masses
            if msg.role == MessageRole.AGENT:
                response_dict = json.loads(last_text.text.value)
                for planet in response_dict["planets"]:
                    print(f"The mass of {planet['name']} is {planet['mass']} kg.")
