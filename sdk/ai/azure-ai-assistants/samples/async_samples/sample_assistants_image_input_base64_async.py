# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use basic assistant operations using image file input for the
    the Azure Assistants service using a synchronous client.

USAGE:
    python sample_assistants_image_input_base64.py

    Before running the sample:

    pip install azure-ai-projects azure-identity

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - the Azure AI Assistants endpoint.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in 
       the "Models + endpoints" tab in your Azure AI Foundry project.
"""
import asyncio
import os, time, base64
from typing import List
from azure.ai.assistants.aio import AssistantsClient
from azure.identity.aio import DefaultAzureCredential
from azure.ai.assistants.models import (
    MessageTextContent,
    MessageInputContentBlock,
    MessageImageUrlParam,
    MessageInputTextBlock,
    MessageInputImageUrlBlock,
)


def image_to_base64(image_path: str) -> str:
    """
    Convert an image file to a Base64-encoded string.

    :param image_path: The path to the image file (e.g. 'image_file.png')
    :return: A Base64-encoded string representing the image.
    :raises FileNotFoundError: If the provided file path does not exist.
    :raises OSError: If there's an error reading the file.
    """
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"File not found at: {image_path}")

    try:
        with open(image_path, "rb") as image_file:
            file_data = image_file.read()
        return base64.b64encode(file_data).decode("utf-8")
    except Exception as exc:
        raise OSError(f"Error reading file '{image_path}'") from exc


async def main():
    async with DefaultAzureCredential() as creds:
        async with AssistantsClient(endpoint=os.environ["PROJECT_ENDPOINT"], credential=creds) as assistants_client:

            assistant = await assistants_client.create_assistant(
                model=os.environ["MODEL_DEPLOYMENT_NAME"],
                name="my-assistant",
                instructions="You are helpful assistant",
            )
            print(f"Created assistant, assistant ID: {assistant.id}")

            thread = await assistants_client.create_thread()
            print(f"Created thread, thread ID: {thread.id}")

            input_message = "Hello, what is in the image ?"
            image_base64 = image_to_base64("../image_file.png")
            img_url = f"data:image/png;base64,{image_base64}"
            url_param = MessageImageUrlParam(url=img_url, detail="high")
            content_blocks: List[MessageInputContentBlock] = [
                MessageInputTextBlock(text=input_message),
                MessageInputImageUrlBlock(image_url=url_param),
            ]
            message = await assistants_client.create_message(thread_id=thread.id, role="user", content=content_blocks)
            print(f"Created message, message ID: {message.id}")

            run = await assistants_client.create_run(thread_id=thread.id, assistant_id=assistant.id)

            # Poll the run as long as run status is queued or in progress
            while run.status in ["queued", "in_progress", "requires_action"]:
                # Wait for a second
                time.sleep(1)
                run = await assistants_client.get_run(thread_id=thread.id, run_id=run.id)
                print(f"Run status: {run.status}")

            if run.status == "failed":
                print(f"Run failed: {run.last_error}")

            await assistants_client.delete_assistant(assistant.id)
            print("Deleted assistant")

            messages = await assistants_client.list_messages(thread_id=thread.id)

            # The messages are following in the reverse order,
            # we will iterate them and output only text contents.
            for data_point in reversed(messages.data):
                last_message_content = data_point.content[-1]
                if isinstance(last_message_content, MessageTextContent):
                    print(f"{data_point.role}: {last_message_content.text.value}")

            print(f"Messages: {messages}")


if __name__ == "__main__":
    asyncio.run(main())
