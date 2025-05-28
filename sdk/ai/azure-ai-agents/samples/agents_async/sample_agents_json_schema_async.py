# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use agents with JSON schema output format.

USAGE:
    python sample_agents_json_schema_async.py

    Before running the sample:

    pip install azure-ai-agents azure-identity pydantic

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
                          page of your Azure AI Foundry portal.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
"""

import asyncio
import os

from enum import Enum
from pydantic import BaseModel, TypeAdapter
from azure.ai.agents.aio import AgentsClient
from azure.identity.aio import DefaultAzureCredential
from azure.ai.agents.models import (
    ListSortOrder,
    MessageTextContent,
    MessageRole,
    ResponseFormatJsonSchema,
    ResponseFormatJsonSchemaType,
    RunStatus,
)


# Create the pydantic model to represent the planet names and there masses.
class Planets(str, Enum):
    Earth = "Earth"
    Mars = "Mars"
    Jupyter = "Jupyter"


class Planet(BaseModel):
    planet: Planets
    mass: float


async def main():
    async with DefaultAzureCredential() as creds:
        async with AgentsClient(
            endpoint=os.environ["PROJECT_ENDPOINT"],
            credential=creds,
        ) as agents_client:

            agent = await agents_client.create_agent(
                model=os.environ["MODEL_DEPLOYMENT_NAME"],
                name="my-agent",
                instructions="Extract the information about planets.",
                response_format=ResponseFormatJsonSchemaType(
                    json_schema=ResponseFormatJsonSchema(
                        name="planet_mass",
                        description="Extract planet mass.",
                        schema=Planet.model_json_schema(),
                    )
                ),
            )
            print(f"Created agent, agent ID: {agent.id}")

            thread = await agents_client.threads.create()
            print(f"Created thread, thread ID: {thread.id}")

            message = await agents_client.messages.create(
                thread_id=thread.id,
                role="user",
                content=("The mass of the Mars is 6.4171E23 kg; the mass of the Earth is 5.972168E24 kg;"),
            )
            print(f"Created message, message ID: {message.id}")

            run = await agents_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)

            if run.status != RunStatus.COMPLETED:
                print(f"The run did not succeed: {run.status=}.")

            await agents_client.delete_agent(agent.id)
            print("Deleted agent")

            messages = agents_client.messages.list(
                thread_id=thread.id,
                order=ListSortOrder.ASCENDING,
            )

            async for msg in messages:
                if msg.role == MessageRole.AGENT:
                    last_part = msg.content[-1]
                    if isinstance(last_part, MessageTextContent):
                        planet = TypeAdapter(Planet).validate_json(last_part.text.value)
                        print(f"The mass of {planet.planet} is {planet.mass} kg.")


if __name__ == "__main__":
    asyncio.run(main())
