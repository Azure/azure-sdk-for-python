# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use assistants with JSON schema output format.

USAGE:
    python sample_assistants_json_schema_async.py

    Before running the sample:

    pip install azure-ai-assistants azure-identity pydantic

    Set this environment variables with your own values:
    PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Studio Project.
"""

import asyncio
import os

from enum import Enum
from pydantic import BaseModel, TypeAdapter
from azure.ai.assistants.aio import AssistantsClient
from azure.identity.aio import DefaultAzureCredential
from azure.ai.assistants.models import (
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
        async with AssistantsClient.from_connection_string(
            credential=creds,
            conn_str=os.environ["PROJECT_CONNECTION_STRING"],
        ) as assistants_client:

            # [START create_assistant]
            assistant = await assistants_client.create_assistant(
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
            # [END create_assistant]
            print(f"Created assistant, assistant ID: {assistant.id}")

            # [START create_thread]
            thread = await assistants_client.create_thread()
            # [END create_thread]
            print(f"Created thread, thread ID: {thread.id}")

            # [START create_message]
            message = await assistants_client.create_message(
                thread_id=thread.id,
                role="user",
                content=("The mass of the Mars is 6.4171E23 kg; the mass of the Earth is 5.972168E24 kg;"),
            )
            # [END create_message]
            print(f"Created message, message ID: {message.id}")

            # [START create_run]
            run = await assistants_client.create_and_process_run(thread_id=thread.id, assistant_id=assistant.id)

            if run.status != RunStatus.COMPLETED:
                print(f"The run did not succeed: {run.status=}.")

            await assistants_client.delete_assistant(assistant.id)
            print("Deleted assistant")

            # [START list_messages]
            messages = await assistants_client.list_messages(thread_id=thread.id)

            # The messages are following in the reverse order,
            # we will iterate them and output only text contents.
            for data_point in reversed(messages.data):
                last_message_content = data_point.content[-1]
                # We will only list assistant responses here.
                if isinstance(last_message_content, MessageTextContent) and data_point.role == MessageRole.ASSISTANT:
                    planet = TypeAdapter(Planet).validate_json(last_message_content.text.value)
                    print(f"The mass of {planet.planet} is {planet.mass} kg.")

            # [END list_messages]


if __name__ == "__main__":
    asyncio.run(main())
