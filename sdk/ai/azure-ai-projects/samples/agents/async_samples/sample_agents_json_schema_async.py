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

    pip install azure-ai-projects azure-identity pydantic

    Set this environment variables with your own values:
    PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Studio Project.
"""

import asyncio
import os

from enum import Enum
from pydantic import BaseModel, TypeAdapter
from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.models import (
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
        async with AIProjectClient.from_connection_string(
            credential=creds,
            conn_str=os.environ["PROJECT_CONNECTION_STRING"],
        ) as project_client:

            # [START create_agent]
            agent = await project_client.agents.create_agent(
                # Note only gpt-4o-mini-2024-07-18 and
                # gpt-4o-2024-08-06 and later support structured output.
                model=os.environ["MODEL_DEPLOYMENT_NAME"],
                name="my-assistant",
                instructions="Extract the information about planets.",
                headers={"x-ms-enable-preview": "true"},
                response_format=ResponseFormatJsonSchemaType(
                    json_schema=ResponseFormatJsonSchema(
                        name="planet_mass",
                        description="Extract planet mass.",
                        schema=Planet.model_json_schema(),
                    )
                ),
            )
            # [END create_agent]
            print(f"Created agent, agent ID: {agent.id}")

            # [START create_thread]
            thread = await project_client.agents.create_thread()
            # [END create_thread]
            print(f"Created thread, thread ID: {thread.id}")

            # [START create_message]
            message = await project_client.agents.create_message(
                thread_id=thread.id,
                role="user",
                content=("The mass of the Mars is 6.4171E23 kg; the mass of the Earth is 5.972168E24 kg;"),
            )
            # [END create_message]
            print(f"Created message, message ID: {message.id}")

            # [START create_run]
            run = await project_client.agents.create_and_process_run(thread_id=thread.id, assistant_id=agent.id)

            if run.status != RunStatus.COMPLETED:
                print(f"The run did not succeed: {run.status=}.")

            await project_client.agents.delete_agent(agent.id)
            print("Deleted agent")

            # [START list_messages]
            messages = await project_client.agents.list_messages(thread_id=thread.id)

            # The messages are following in the reverse order,
            # we will iterate them and output only text contents.
            for data_point in reversed(messages.data):
                last_message_content = data_point.content[-1]
                # We will only list agent responses here.
                if isinstance(last_message_content, MessageTextContent) and data_point.role == MessageRole.AGENT:
                    planet = TypeAdapter(Planet).validate_json(last_message_content.text.value)
                    print(f"The mass of {planet.planet} is {planet.mass} kg.")

            # [END list_messages]


if __name__ == "__main__":
    asyncio.run(main())
