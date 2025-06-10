# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to get a chat completions streaming response from
    the service using an asynchronous client, with an Azure OpenAI (AOAI) endpoint.
    Two types of authentications are shown: key authentication and Entra ID
    authentication.

USAGE:
    1. Update `key_auth` below to `True` for key authentication, or `False` for
       Entra ID authentication.
    2. Update `api_version` (the AOAI REST API version) as needed.
       See the "Data plane - inference" row in the table here for latest AOAI api-version:
       https://aka.ms/azsdk/azure-ai-inference/azure-openai-api-versions
    3. Set one or two environment variables, depending on your authentication method:
        * AZURE_OPENAI_CHAT_ENDPOINT - Your AOAI endpoint URL, with partial path, in the form
            https://<your-unique-resouce-name>.openai.azure.com/openai/deployments/<your-deployment-name>
            where `your-unique-resource-name` is your globally unique AOAI resource name,
            and `your-deployment-name` is your AI Model deployment name.
            For example: https://your-unique-host.openai.azure.com/openai/deployments/gpt-4o
        * AZURE_OPENAI_CHAT_KEY - Your model key. Keep it secret. This
            is only required for key authentication.
    4. Run the sample:
       python sample_chat_completions_streaming_azure_openai_async.py
"""
import asyncio


async def sample_chat_completions_streaming_azure_openai_async():
    import os
    from azure.ai.inference.aio import ChatCompletionsClient
    from azure.ai.inference.models import SystemMessage, UserMessage

    try:
        endpoint = os.environ["AZURE_OPENAI_CHAT_ENDPOINT"]
    except KeyError:
        print("Missing environment variable 'AZURE_OPENAI_CHAT_ENDPOINT'")
        print("Set it before running this sample.")
        exit()

    key_auth = True  # Set to True for key authentication, or False for Entra ID authentication.

    if key_auth:
        from azure.core.credentials import AzureKeyCredential

        try:
            key = os.environ["AZURE_OPENAI_CHAT_KEY"]
        except KeyError:
            print("Missing environment variable 'AZURE_OPENAI_CHAT_KEY'")
            print("Set it before running this sample.")
            exit()

        client = ChatCompletionsClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(key),
            api_version="2024-06-01",  # Azure OpenAI api-version. See https://aka.ms/azsdk/azure-ai-inference/azure-openai-api-versions
        )

    else:  # Entra ID authentication
        from azure.identity.aio import DefaultAzureCredential

        client = ChatCompletionsClient(
            endpoint=endpoint,
            credential=DefaultAzureCredential(),
            credential_scopes=["https://cognitiveservices.azure.com/.default"],
            api_version="2024-06-01",  # Azure OpenAI api-version. See https://aka.ms/azsdk/azure-ai-inference/azure-openai-api-versions
        )

    response = await client.complete(
        stream=True,
        messages=[
            SystemMessage("You are a helpful assistant."),
            UserMessage("Give me 5 good reasons why I should exercise every day."),
        ],
    )

    # Iterate on the response to get chat completion updates, as they arrive from the service
    async for update in response:
        if update.choices and update.choices[0].delta:
            print(update.choices[0].delta.content or "", end="", flush=True)
        if update.usage:
            print(f"\n\nToken usage: {update.usage}")

    await client.close()


async def main():
    await sample_chat_completions_streaming_azure_openai_async()


if __name__ == "__main__":
    asyncio.run(main())
